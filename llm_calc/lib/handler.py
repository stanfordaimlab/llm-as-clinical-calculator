from sys import exception

from humanfriendly.terminal import output
from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable
from pydantic import BaseModel
from langchain.agents import AgentExecutor

from llm_calc.lib.datacore import datacore
from llm_calc.tools.structured_output import StructuredResponse
from llm_calc.util import util
from typing import Any
from typing import List, Optional
from enum import Enum
from pydantic.dataclasses import dataclass
from llm_calc.lib.datamodel import LLMResult, ModelSlug, Case, CalculatorSlug, ArmSlug
import traceback

from langchain_core.runnables import RunnablePassthrough, Runnable

from llm_calc.util.util import coerce_json_decode
from llm_calc.lib.config import config
import json
from llm_calc.lib.datamodel import Experiment

# ---------------- handler ----------------


class LLMHandler(BaseModel):
    """
    This class is used to handle the LLMs Agents to format the input and output
    and handle errors.
    :param executor: runnable such as chain or AgentExecutor
    """

    _chain_execution_func: Any
    _arm_slug: ArmSlug
    _experiment: Any

    def __init__(
        self,
        chain_execution_func: Any,
        experiment: Any,
        arm_slug: ArmSlug,
        /,
        **data: Any,
    ):
        super().__init__(**data)
        self._chain_execution_func = chain_execution_func
        self._arm_slug = arm_slug
        self._experiment = experiment

    @traceable
    def execute(self, inputs: dict) -> Any:
        """
        Invoke the agent executor with the given human_input
        """

        # from IPython import embed
        # embed()

        # if case is provided, add it to the human_input
        # unclear what the encoding is for this (not json)
        case_string = inputs["additional_case_details_all_case_details"]
        # use json
        case_json = inputs["additional_case_details_all_case_details_json"]
        case_dict = json.loads(case_json)
        case = Case(**case_dict)

        # formatted_options = {}
        # options = inputs["additional_case_details_options"]
        # if case.calculator_slug == CalculatorSlug.nihss:
        #     options = json.loads("{" + options + "}")
        #     formatted_options = {
        #         "consciousness": options["consciousness"],
        #         "questions": options["questions"],
        #         "commands": options["commands"],
        #         "gaze": options["gaze"],
        #         "visual": options["visual"],
        #         "facial_palsy": options["facial_palsy"],
        #         "motor_arm_left": options["motor_arm_left"],
        #         "motor_arm_right": options["motor_arm_right"],
        #         "motor_leg_left": options["motor_leg_left"],
        #         "motor_leg_right": options["motor_leg_right"],
        #         "limb_ataxia": options["limb_ataxia"],
        #         "sensory": options["sensory"],
        #         "language": options["language"],
        #         "dysarthria": options["dysarthria"],
        #         "extinction": options["extinction"],
        #     }
        # else:
        #     formatted_options = options

        # langchain expects a dictionary under the hood, so we need to wrap the human_input
        # "formatted options" here is just a hack for a NIHSS specific debug - viewable from inner-execute trace
        human_input: dict = {"human_input": inputs["human_input"]}

        # Execute the inner function
        inner_result: LLMResult = self.inner_execute(human_input)

        answer, explanation = "", ""
        if inner_result.output_object:
            answer = inner_result.output_object["answer"]
            explanation = inner_result.output_object["explanation"]
        else:
            answer = "Error"
            explanation = "Error"
        case_name = case.name
        case_id = case.id
        inner_result.case = case
        inner_result.arm_slug = self._arm_slug

        # Add experiment to inner_result
        exp: Experiment = self._experiment
        exp.cases = []  # Clear cases to avoid duplication
        exp.end_datetime = util.get_timestamp()
        exp.is_completed = True
        inner_result.experiment = exp

        pretty_output = f"Case #{case_id} {case_name}: {answer} -- {explanation}"
        details = inner_result

        result = {"output": pretty_output, "details": details}

        return result

    @traceable
    def inner_execute(self, human_input: dict) -> LLMResult:
        """
        Invoke the agent executor with the given human_input
        """
        # TODO: clean up, messy code (outputs and attempts too similar)
        import time

        output = LLMResult()
        attempts = []
        exception_messages = []
        num_attempts = 0
        num_error_attempts = 0
        allowed_num_attempts = config.LLM_MAX_NUM_RETRIES

        while num_attempts < allowed_num_attempts:
            attempt = LLMResult()
            num_attempts += 1
            attempt.num_attempts = num_attempts
            try:
                raw_response = self._chain_execution_func(human_input)
                response: StructuredResponse = self.custom_parser(
                    raw_response["output"]
                )

                # get the raw json string
                raw_json_string = response.output.json()

                # since we will be changing the string to coerce it to valid
                # json, we need  to record whether the original LLM output as
                # valid JSON otherwise we lose this information
                attempt.output_string_is_valid_json = util.is_valid_json(
                    raw_json_string
                )
                coerced_output_string = util.coerce_to_valid_json(raw_json_string)

                # if the output is not coercible to valid JSON, then we can't use it; raise an exception
                if not util.is_valid_json(coerced_output_string):
                    raise Exception("Output is not valid JSON even after coercion")
                else:
                    attempt.output_string = coerced_output_string
                    attempt.output_object = util.coerce_json_decode(raw_json_string)

                # if "able to answer" false in the output, then we need to reattempt
                if (
                    attempt.output_object["able_to_answer"] == False
                    or attempt.output_object["able_to_answer"] == "False"
                ) or attempt.output_object["able_to_answer"] == "false":
                    raise Exception(
                        "Unable to answer is recorded as {}".format(
                            attempt.output_object["able_to_answer"]
                        )
                    )

                # record the metadata
                attempt.was_error = False
                attempt.errored_attempts = attempts
                attempt.num_errored_attempts = num_error_attempts
                attempt.raw_response = raw_response
                # attempt.run = raw_response['__run']
                attempt.intermediate_steps = raw_response["intermediate_steps"]
                attempt.human_input = raw_response["human_input"]
                return attempt

            except Exception as e:
                # any error - record the error and reattempt if under max attempts
                util.log(f"Error in LLMHandler.execute: {str(e)}")
                num_error_attempts += 1
                attempt.exception = e
                attempt.exception_message = str(e)
                attempt.exception_traceback = e.__traceback__
                # traceback.print_exc()
                attempt.output_string = "Error"
                attempt.was_error = True
                attempts.append(attempt)
                exception_messages.append(str(e))

                # if rate limit error, sleep for 5 seconds
                if (
                    "rate limit" in attempt.exception_message
                    or "Too Many Requests" in attempt.exception_message
                    or "Rate limit" in attempt.exception_message
                    or "429" in attempt.exception_message
                ):
                    util.log_error(
                        f"Rate limit error - sleeping for {config.LLM_RETRY_SLEEP} seconds"
                    )
                    time.sleep(config.LLM_RETRY_SLEEP)

        # if we have reached the max number of attempts, return the last error
        formatted_exception_messages = "\n- ".join(exception_messages)
        util.log_error(
            f"Max number of attempts { config.LLM_MAX_NUM_RETRIES } reached. Exception "
            f"messages: ",
            formatted_exception_messages,
        )
        output.errored_attempts = attempts
        output.num_errored_attempts = num_error_attempts
        output.num_attempts = num_attempts
        output.was_error = True
        output.output_string = "This was an error at the model level"
        return output

    @staticmethod
    def custom_parser(raw_model_output):
        """
        Custom parser for the LLM output; this is used to coerce the output to valid JSON
        :param raw_model_output:
        :return:
        """

        # attempt to directly parse the output into StructuredResponse buy assigning dicts to the fields
        from llm_calc.tools.structured_output import FinalResponse
        from llm_calc.lib import prompts

        # from IPython import embed; embed()

        try:
            raw_model_output = raw_model_output.content
        except Exception as e:
            pass

        try:
            decoded_output = util.coerce_json_decode(raw_model_output)
            final_response: FinalResponse = FinalResponse(**decoded_output)
            response: StructuredResponse = StructuredResponse(output=final_response)
            return response
        except Exception as e:
            util.log_warning(
                "Warning: Could not directly parse the output into StructuredResponse, "
                "using GPT4o mini parser instead"
            )
            # traceback.print_exc()
            pass

        llm = config.PARSER_LLM
        structured_llm = llm.with_structured_output(StructuredResponse)
        parser_chain = (
            {"raw_model_output": RunnablePassthrough()}
            | prompts.parser_prompt
            | structured_llm
        )
        return parser_chain.invoke({"raw_model_output": raw_model_output})


if __name__ == "__main__":
    print("This file is not meant to be executed")
