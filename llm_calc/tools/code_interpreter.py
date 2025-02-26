# needs prompt engineering a la
# https://dev.to/tereza_tizkova/llama-3-with-function-calling-and-code-interpreter-55nb
import random

from globals import *

from llm_calc.tools.rag import DocumentationRetriever
from llm_calc.util import util
import os
import json
from typing import Any
from langchain_core.tools import Tool
from langchain_core.tools.structured import StructuredTool
from pydantic.v1 import BaseModel, Field
from e2b_code_interpreter import CodeInterpreter
from langchain_core.messages import ToolMessage
from typing import List, Sequence, Tuple
from langchain.agents import AgentExecutor
from langchain_core.messages import BaseMessage
from langchain.agents.output_parsers.tools import (
    ToolAgentAction,
    ToolsAgentOutputParser,
    parse_ai_message_to_tool_action,
)

from typing import List, Union
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import AIMessage
from langchain_core.outputs import Generation, ChatGeneration

from langchain_groq import ChatGroq
from llm_calc.lib.config import config
from llm_calc.lib import prompts
from langchain_core.messages import AIMessage, AIMessageChunk

from langchain_core.agents import AgentFinish, AgentActionMessageLog

from langchain_core.prompts import ChatPromptTemplate

# observability
from langsmith import traceable


# rag
from langchain_core.runnables import RunnablePassthrough, Runnable

from llm_calc.tools.structured_output import FinalResponse


class LangchainCodeInterpreterToolInput(BaseModel):
    code: str = Field(description="Python code to execute.")


class CodeInterpreterTool:
    """
    This class calls arbitrary code against a Python Jupyter notebook.
    It requires an E2B_API_KEY to create a sandbox.
    """

    tool_name: str = "code_interpreter"
    _llm: Any = None
    _chain: Any = None
    _chain_with_rag_only: Any = None
    _chain_with_rag_and_ci: Any = None
    _chain_with_omc: Any = None
    _chain_with_base: Any = None
    _tools: Any = None
    _context: Any = None
    code_interpreter: CodeInterpreter = None
    code_interpreter_array: list = []
    code_interpreter_cursor: int = 0

    def initialize_code_interpreter(self):
        # Instantiate the E2B sandbox - this is a long lived object
        # that's pinging E2B cloud to keep the sandbox alive.
        if "E2B_API_KEY" not in os.environ:
            raise Exception(
                "Code Interpreter tool called while E2B_API_KEY environment variable is not set. Please get your E2B api key here https://e2b.dev/docs and set the E2B_API_KEY environment variable."
            )
        for i in range(0, 20):
            self.code_interpreter_array.append(CodeInterpreter())

        # self.code_interpreter = CodeInterpreter()

    def set_llm(self, llm):
        self._llm = llm

    def initialize_with_llm(
        self, llm: Runnable, prompt: ChatPromptTemplate = None, parser: Any = None
    ) -> bool:
        """
        Initialize the code interpreter tool.
        """
        if llm is not None:
            self.set_llm(llm)
        else:
            self.set_llm(config.DEFAULT_LLM)

        self._chain = self.to_chain()
        return True

    def call(self, parameters: dict, **kwargs: Any):
        code = parameters.get("code", "")
        # util.log_mini_task(f"Code Interpreter called.")
        # print(f"***Code Interpreting...\n{code}\n====")
        execution = None  #
        if self.code_interpreter_cursor >= 20:
            self.code_interpreter_cursor = 0
        else:
            self.code_interpreter_cursor += 1

        i = self.code_interpreter_cursor
        util.log_message(f"Using code interpreter {i}")
        # i = random.sample(range(0, 5), 1)[0]
        execution = self.code_interpreter_array[i].notebook.exec_cell(code)

        return {
            "results": execution.results,
            "stdout": execution.logs.stdout,
            "stderr": execution.logs.stderr,
            "error": execution.error,
        }

    def close_all(self):
        for i in range(0, len(self.code_interpreter_array)):
            self.code_interpreter_array[i].close()

    def close(self):
        self.code_interpreter.close()

    @staticmethod
    def final_response(self, explanation, answer, able_to_answer) -> dict:
        resp = {
            "explanation": explanation,
            "answer": answer,
            "able_to_answer": able_to_answer,
        }
        return resp

    def final_response_tool(self) -> StructuredTool:
        tool = StructuredTool(
            name="final_response",
            description="Submit your final answer to the user's question. Only call this once you've received all the information you need.",
            func=self.final_response,
            args_schema=FinalResponse,
            return_direct=True,
        )
        return tool

    # langchain does not return a dict as a parameter, only a code string
    def langchain_call(self, code: str):
        return self.call({"code": code})

    def to_langchain_tool(self) -> Tool:
        tool = Tool(
            name=self.tool_name,
            description="Execute python code in a Jupyter notebook cell and returns any rich data (eg charts), stdout, stderr, and error.",
            func=self.langchain_call,
        )
        tool.args_schema = LangchainCodeInterpreterToolInput
        return tool

    def to_chain(self) -> Runnable:
        """
        Creation of tool through to_langchain_tool preferred.
        Create a LangChain runnable that can be used to execute the code interpreter tool using default parameters.
        :return: agent executor
        """
        tools = [self.to_langchain_tool(), self.final_response_tool()]
        self._tools = tools
        prompt = prompts.ci_prompt
        llm = self._llm

        agent = (
            RunnablePassthrough.assign(
                agent_scratchpad=lambda x: format_to_tool_messages(
                    x["intermediate_steps"]
                )
            )
            | prompt
            | llm.bind_tools(tools, parallel_tool_calls=False)
            | ExtendedToolsAgentOutputParser()
        )
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=config.AGENTS_ARE_VERBOSE,
            return_intermediate_steps=True,
        )
        return agent_executor

    def initialize_rag_tool(self):
        """
        Initialize the RAG tool as a part of the chain
        """
        self._chain_with_rag_only = self.to_chain_with_rag_only()
        self._chain_with_rag_and_ci = self.to_chain_with_rag_and_ci()
        return True

    def initialize_omc_tool(self):
        """
        Initialize the OpenMedCalc tool as a part of the chain
        """
        self._chain_with_omc = self.to_chain_with_omc()
        return True

    def initialize_base_tool(self):
        """
        Initialize the Base tool as a part of the chain
        """
        self._chain_with_base = self.to_chain_base()
        return True

    def to_chain_with_rag_and_ci(self):
        """
        Created a chain that includes both the Code Interpreter
        and RAG as a tool. The agent can ?choose which tools to use
        :return:
        """
        from llm_calc.tools.rag import DocumentationRetriever
        from operator import itemgetter

        llm = self._llm
        if llm is None:
            raise Exception("LLM not set. Please set the LLM to use with this tool")

        # Initialize the RAG tool
        r = DocumentationRetriever()
        r.initialize_with_llm(self._llm)

        # Create the chain with both tools
        tools = [self.to_langchain_tool(), self.final_response_tool()]
        prompt: ChatPromptTemplate = prompts.ci_rag_prompt

        agent = (
            RunnablePassthrough.assign(
                context=itemgetter("human_input") | r.retriever | r.format_docs
            )
            | RunnablePassthrough.assign(
                agent_scratchpad=lambda x: format_to_tool_messages(
                    x["intermediate_steps"]
                )
            )
            | prompt
            | llm.bind_tools(tools, parallel_tool_calls=False)
            | ExtendedToolsAgentOutputParser()
        )
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=config.AGENTS_ARE_VERBOSE,
            return_intermediate_steps=True,
        )
        return agent_executor

    def to_chain_with_rag_only(self):
        """
        Created a chain that includes both the Code Interpreter
        and RAG as a tool. The agent can ?choose which tools to use
        :return:
        """
        from llm_calc.tools.rag import DocumentationRetriever
        from operator import itemgetter

        llm = self._llm
        if llm is None:
            raise Exception("LLM not set. Please set the LLM to use with this tool")

        # Initialize the RAG tool
        r = DocumentationRetriever()
        r.initialize_with_llm(self._llm)

        # Create the chain with both tools
        tools = [self.final_response_tool()]
        prompt: ChatPromptTemplate = prompts.rag_prompt

        agent = (
            RunnablePassthrough.assign(
                context=itemgetter("human_input") | r.retriever | r.format_docs
            )
            | RunnablePassthrough.assign(
                agent_scratchpad=lambda x: format_to_tool_messages(
                    x["intermediate_steps"]
                )
            )
            | prompt
            | llm.bind_tools(tools, parallel_tool_calls=False)
            | ExtendedToolsAgentOutputParser()
        )
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=config.AGENTS_ARE_VERBOSE,
            return_intermediate_steps=True,
        )
        return agent_executor

    def to_chain_base(self):
        """
        Should only have access to final answer tool; no actual code interpreter
        :return:
        """
        from llm_calc.tools.rag import DocumentationRetriever
        from operator import itemgetter

        llm = self._llm
        if llm is None:
            raise Exception("LLM not set. Please set the LLM to use with this tool")

        # Create the chain with both tools
        tools = [self.final_response_tool()]
        prompt: ChatPromptTemplate = prompts.base_prompt

        agent = (
            RunnablePassthrough.assign(
                agent_scratchpad=lambda x: format_to_tool_messages(
                    x["intermediate_steps"]
                )
            )
            | prompt
            | llm.bind_tools(tools, parallel_tool_calls=False)
            | ExtendedToolsAgentOutputParser()
        )
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=config.AGENTS_ARE_VERBOSE,
            return_intermediate_steps=True,
        )
        return agent_executor

    def to_chain_with_omc(self):
        """
        Created a chain that includes both the Code Interpreter
        and OpenMedCalc as a tool. The agent can ?choose which tools to use
        :return:
        """
        from llm_calc.tools.openmedcalc.calculators_as_tools import omc_toolkit_all
        from llm_calc.tools.openmedcalc.calculators_as_tools import omc_toolkit_by_name

        llm = self._llm
        if llm is None:
            raise Exception("LLM not set. Please set the LLM to use with this tool")

        # Create the chain with tools
        tools = [*omc_toolkit_all, self.final_response_tool()]
        prompt = prompts.omc_prompt

        agent = (
            RunnablePassthrough.assign(
                agent_scratchpad=lambda x: format_to_tool_messages(
                    x["intermediate_steps"]
                )
            )
            | prompt
            | llm.bind_tools(tools, parallel_tool_calls=False)
            | ExtendedToolsAgentOutputParser()
        )
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=config.AGENTS_ARE_VERBOSE,
            return_intermediate_steps=True,
        )
        return agent_executor

    def execute(self, human_input) -> str:
        """
        Creation of tool through to_langchain_tool preferred.
        Create a LangChain runnable, invoke and return the results.
        :return: outputs
        """

        if self._chain_with_rag_only is not None:
            util.log("Using combined CI-RAG tool as RAG is active.")
            output = self.execute_with_rag_and_ci(human_input)
        elif self._chain_with_omc is not None:
            util.log("Using combined OMC tool as OMC is active.")
            output = self.execute_with_omc(human_input)
        else:
            output = self._chain.invoke(human_input)

        # check if output has a key called output
        return output
        # if "output" in output:
        #     return output["output"]
        # else:
        #     return str(output)

    def execute_with_rag_and_ci(self, human_input) -> str:
        """
        Creation of tool through to_langchain_tool preferred.
        Create a LangChain runnable, invoke and return the results.
        :return: outputs
        """

        # Initialize the RAG tool
        # r = DocumentationRetriever()
        # r.initialize_with_llm(self._llm)

        output = self._chain_with_rag_and_ci.invoke(human_input)
        return output

    def execute_with_rag_only(self, human_input) -> str:
        """
        Creation of tool through to_langchain_tool preferred.
        Create a LangChain runnable, invoke and return the results.
        :return: outputs
        """

        #  # Initialize the RAG tool
        # r = DocumentationRetriever()
        # r.initialize_with_llm(self._llm)

        output = self._chain_with_rag_only.invoke(human_input)
        return output

    def execute_with_base(self, human_input) -> str:
        """ """
        output = self._chain_with_base.invoke(human_input)

        return output

    def execute_with_omc(self, human_input) -> str:
        """ """
        output = self._chain_with_omc.invoke(human_input, include_run_info=True)

        return output
        # check if output has a key called output
        # if "output" in output:
        #     return output["output"]
        # else:
        #     return str(output)

    @staticmethod
    def format_to_tool_message(
        agent_action: ToolAgentAction,
        observation: dict,
    ) -> List[BaseMessage]:
        """
        Format the output of the CodeInterpreter tool to be returned as a ToolMessage.
        """
        new_messages = list(agent_action.message_log)

        # TODO: Returns the "result" (returned value from cell) generally as list of Class Result
        if isinstance(observation["results"], list):
            observation["results"] = [obs.text for obs in observation["results"]]
        else:
            observation["results"] = observation["results"].text

        if observation["error"] is not None:
            error: Any = observation["error"]
            new_val = str(error)
            stripped = util.strip_all_non_alphanum(new_val)
            util.log_warning(f"Error new val: {new_val}")
            content = json.dumps(
                {"results": [], "stdout": [], "stderr": [], "error": new_val}
            )
        else:
            content = json.dumps(
                # {k: v for k, v in observation.items()}, indent=2
                {k: v for k, v in observation.items()},
                indent=2,
                skipkeys=True,
            )

        new_messages.append(
            ToolMessage(content=content, tool_call_id=agent_action.tool_call_id)
        )
        return new_messages


# output formatter
@traceable
def format_to_tool_messages(
    intermediate_steps: Sequence[Tuple[ToolAgentAction, dict]],
) -> List[BaseMessage]:
    messages = []
    for agent_action, observation in intermediate_steps:
        if agent_action.tool == CodeInterpreterTool.tool_name:
            new_messages = CodeInterpreterTool.format_to_tool_message(
                agent_action,
                observation,
            )
            messages.extend([new for new in new_messages if new not in messages])
        elif agent_action.tool == "information_about_medical_calculator":
            # DocumentationRetriever().get_retriever_tool().name:
            new_messages = DocumentationRetriever.format_to_tool_message(
                agent_action,
                observation,
            )
            messages.extend([new for new in new_messages if new not in messages])

        else:
            # Handle other tools
            # print("Now handling tool: ", agent_action.tool)
            new_messages = DocumentationRetriever.format_to_tool_message(
                agent_action,
                observation,
            )
            messages.extend([new for new in new_messages if new not in messages])

    return messages


class ExtendedToolsAgentOutputParser(ToolsAgentOutputParser):
    """
    An extended version of ToolsAgentOutputParser that includes all the same
    methods and properties of the original class.
    """

    @property
    def _type(self) -> str:
        return "extended-tools-agent-output-parser"

    def parse_result(
        self, result: List[Generation], *, partial: bool = False
    ) -> Union[List[AgentAction], AgentFinish]:
        if not isinstance(result[0], ChatGeneration):
            raise ValueError("This output parser only works on ChatGeneration output")
        message = result[0].message

        # from IPython import embed; embed()

        # If there are multiple tool calls, remove all but the first one
        if len(message.tool_calls) > 1:
            util.log_warning(
                "Multiple tool calls detected. Will only execute the first one."
            )
            message.tool_calls = message.tool_calls[:1]

        try:
            if message.additional_kwargs["tool_calls"]:
                tool_call = message.additional_kwargs["tool_calls"][0]
                function = tool_call["function"]
                function_name = function["name"]
                inputs = {"output": json.loads(function["arguments"])}
                if function_name == "final_response":
                    return AgentFinish(return_values=inputs, log=str(function))
        except Exception as e:
            util.log(f"Error parsing tool call: {e}")
            pass

        return parse_ai_message_to_tool_action(message)

    def parse(self, text: str) -> Union[List[AgentAction], AgentFinish]:
        raise ValueError("Can only parse messages")
