import json

from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

# ------------------------------------- system prompts ---------------------------------------
# These prompts are used to introduce the system to the user and provide context for the task.
# Formatting instructions are also included in the system prompts,
# addended to the end of the prompt text below.


_introduction = """
# Introduction
You are an assistant for medical question-answering tasks focusing on medical calculation. The user will prompt you with a question about a clinical calculation that they would like to have help with. If you do not have all information required to complete the calculation, do your best. You will not be allowed to ask clarifying questions. When you are ready to provide an answer, use the provided final_response tool to submit your answer. 
"""


_base_system_prompt_tools = """
"""

_rag_system_prompt_tools = """
# Available Tools/Resources
- As discussed above, the final_response tool is used to submit your answer.
- In addition, you have access to the following high-quality information regarding how to perform the calculation in the question (see "provided context")

# Provided Context
{context}
"""

_ci_system_prompt_tools = """
# Available Tools/Resources
- You have a code_interpreter tool at your disposal; this allows you to run python code snippets in a Jupyter notebook-like environment. Use this tool to assist in answering the user's question. It is required to use this tool.
- Do not call multiple tools at once, but use them in a stepwise manner.
- As discussed above, the final_response tool is used to submit your answer.
"""

_ci_rag_system_prompt_tools = """
# Available Tools/Resources
- You have a code_interpreter tool at your disposal; this allows you to run python code snippets in a Jupyter notebook-like environment. Use this tool, if needed, to assist in answering the user's question. It is required to use this tool.
- Do not call multiple tools at once, but use them in a stepwise manner.
- As discussed above, the final_response tool is used to submit your answer.
- In addition, you have access to the following high-quality information regarding how to perform the calculation in question (see "provided context"). 


# Provided Context
{context}
"""

_omc_system_prompt_tools = """
# Available Tools/Resources
- To answer the user's questions, you have access to a set of calculators that help you perform medical calculations. Your first response should call one of these tools.
- If you receive an error from one of these functions, you can try again again after correcting for the formatting error. 
- Do not call multiple tools at once, but use them in a stepwise manner, waiting to receive a response from the first tool before calling the next.
- As discussed above, the final_response tool is used to submit your answer. 

# Caution
- Pay close attention to the details of the reponse you provide, paying special attention to the details of the fields required by the tools.
- For example, if an input field is denoted as "renal disease," but the description of the field specifies that the patient only neets this cirteria if they have a creatinine of 2.2 or greater, you must ensure that the details are correct.
"""

# _omc_system_prompt_tools = """
# # Available Tools/Resources
# - PLEASE HELP US TEST THESE TOOLS BY CALLING THEM WITH INCOMPLETE INPUTS.
# """


# ------------------------------ add introductions  ---------------------------------

_base_system_prompt = _introduction + _base_system_prompt_tools
_rag_system_prompt = _introduction + _rag_system_prompt_tools
_ci_system_prompt = _introduction + _ci_system_prompt_tools
_ci_rag_system_prompt = _introduction + _ci_rag_system_prompt_tools
_omc_system_prompt = _introduction + _omc_system_prompt_tools


# ------------------------------ add formatting instructions  ---------------------------------

# _formatting_instructions= '''
# # Formatting Instructions
# Your final answer should be formatted in JSON as follows:
#
# {{ "explanation": "Eight minus five is equal to three",
# "answer": 3,
# "able_to_answer" : false
#  }}
#
# Explanation, string: containing your rationale for the answer.
# Answer, float or false: the final answer to the user's query.
# able_to_answer, boolean: whether or not you were able to answer the user's query.
#
# Final answers that are not valid JSON in this format will be refused.
# '''
#
#
# _base_system_prompt += _formatting_instructions
# _rag_system_prompt += _formatting_instructions
# _ci_system_prompt += _formatting_instructions
# _ci_rag_system_prompt += _formatting_instructions
# _omc_system_prompt += _formatting_instructions


# ------------------------------ add prompt engineering  ---------------------------------

_prompt_engineering_rewards = """
# Rewards and Penalties
- The responses you provide will be used for patient care. A correct answer is critical, and miscalculations can lead to serious consequences, including the death of patients. Therefore, you are expected to provide accurate and reliable answers.
- If you provide only correct answers, you will receive a reward of $2000.
- If you provide an incorrect answer, you will be not receive any reward. In addition, you will be held liable for any consequences that arise from your response, including potential legal action, loss of your position, and a fee not to exceed $215,000. 
"""

_prompt_engineering = f"{_prompt_engineering_rewards}"

_base_system_prompt += _prompt_engineering
_rag_system_prompt += _prompt_engineering
_ci_system_prompt += _prompt_engineering
_ci_rag_system_prompt += _prompt_engineering
_omc_system_prompt += _prompt_engineering


# ------------------------------------ examples -------------------------------------------------


# ----------- example 1 -----------

example1_input = [
    HumanMessage(
        """
I have a patient with whom I'd like your assistance. The patient is a 45-year-old man admitted to the hospital with hypertensive emergency. His blood pressure is 220/120.  He has no history of stroke or transient ischemic attack. Based on this most recent BP reading, what is his MAP?
"""
    )
]


example1_ci_tool_use = [
    AIMessage(
        content="I'm going to use the code_interpreter tool to calculate the MAP based on the given parameters.",
        tool_calls=[
            {
                "name": "code_interpreter",
                "args": {
                    "code": "import math\n\n# Given values systolic = 220, diastolic = 120\nsystolic = 220\ndiastolic = 120\n\n# Calculate MAP\nMAP = (1/3) * systolic + (2/3) * diastolic\n\nMAP"
                },
                "id": "call_gxJbBCXu1gEhBXgf7g12nT69",
            }
        ],
    ),
    ToolMessage("154", tool_call_id="call_gxJbBCXu1gEhBXgf7g12nT69"),
]

example1_omc_tool_output = {
    "Information": {
        "success": True,
        "score": 154,
        "message": "The MAP is estimated to be 154 mmHg.",
        "additional_info": "See https://openmedcalc.org/map for references. ",
    }
}

example1_omc_tool_use = [
    AIMessage(
        "I'm going to use the calculate_map tool to calculate the MAP based on the given parameters.",
        tool_calls=[
            {
                "name": "calculate_map",
                "args": {"systolic": 220, "diastolic": 120},
                "id": "call_gxJbBCXu1gEhBXgf7g12nT69",
            }
        ],
    ),
    ToolMessage(
        content=json.dumps(example1_omc_tool_output),
        tool_call_id="call_gxJbBCXu1gEhBXgf7g12nT69",
    ),
]

example1_final_output_dict = {
    "explanation": "A common manner for estimation of mean arterial pressure (MAP) involves calculating "
    "the sum of twice the diastolic blood pressure and the systolic blood pressure, "
    "divided by 3. Or, in other words: MAP = 1/3*(SBP) + 2/3*(DBP)",
    "answer": 154,
    "able_to_answer": True,
}

example1_final_response_tool_use = [
    AIMessage(
        "Based on the information provided, I can estimate the MAP and will submit the final response.",
        tool_calls=[
            {
                "name": "final_response",
                "args": example1_final_output_dict,
                "id": "call_234lkjjddds12",
            }
        ],
    ),
    ToolMessage(
        content="Correct answer. Your account has been deposited with your reward.",
        tool_call_id="call_234lkjjddds12",
    ),
]

# ----------- example 2 -----------


example2_input = [
    HumanMessage(
        "I need help with a clinical calculation. I have a 65-year-old admitted to the hospital for a total knee replacement, but her anesthesiologist is concerned about her blood pressure; her systolic blood pressure is 160. What is her MAP?"
    )
]

example2_final_output_dict = {
    "explanation": "Mean arterial pressure (MAP) is calculated as the sum of twice the diastolic blood pressure and the systolic blood pressure, divided by 3. Without the diastolic blood  pressure, we are unable to estimate the MAP.",
    "answer": False,
    "able_to_answer": False,
}

example2_final_output = [AIMessage(f"{example2_final_output_dict}")]


# ------------------------------------ templates -------------------------------------------------

_base_prompt_template = [
    ("system", _base_system_prompt),
    *(example1_input + example1_final_response_tool_use),
    # *(example2_input + example2_final_output),
    ("human", "{human_input}"),
]

_rag_prompt_template = [
    ("system", _rag_system_prompt),
    *(example1_input + example1_final_response_tool_use),
    # *(example2_input + example2_final_output),
    ("human", "{human_input}"),
]

_ci_prompt_template = [
    ("system", _ci_system_prompt),
    *(example1_input + example1_ci_tool_use + example1_final_response_tool_use),
    # *(example2_input + example2_final_output),
    ("human", "{human_input}"),
    ("placeholder", "{agent_scratchpad}"),
]

_ci_rag_prompt_template = [
    ("system", _ci_rag_system_prompt),
    *(example1_input + example1_ci_tool_use + example1_final_response_tool_use),
    # *(example2_input + example2_final_output),
    ("human", "{human_input}"),
    ("placeholder", "{agent_scratchpad}"),
]

_omc_prompt_template = [
    ("system", _omc_system_prompt),
    *(example1_input + example1_omc_tool_use + example1_final_response_tool_use),
    # *(example2_input + example2_final_output),
    ("human", "{human_input}"),
    ("placeholder", "{agent_scratchpad}"),
]


# ------------------------------------ final prompts ----------------------------------------------

base_prompt = ChatPromptTemplate.from_messages(messages=_base_prompt_template)
rag_prompt = ChatPromptTemplate.from_messages(messages=_rag_prompt_template)
ci_prompt = ChatPromptTemplate.from_messages(messages=_ci_prompt_template)
ci_rag_prompt = ChatPromptTemplate.from_messages(messages=_ci_rag_prompt_template)
omc_prompt = ChatPromptTemplate.from_messages(messages=_omc_prompt_template)


# ------------------------------------ parser prompts -------------------------------------------------

_parser_template = [
    (
        "system",
        "You are a JSON extraction/formatting expert. Examine the following output for "
        "something that resembles an answer to a medical calculation question. If it appears that the content provided contains a numeric answer,"
        "extract into a JSON object with the fields in the given format."
        "If you cannot find an answer, or see that the content is asking a question, refuses to answer the question, "
        "or says the question is not answerable, then return an object"
        "with an answer of 0, able_to_answer of false, and an explanation containing the phrase 'Model did not produce valid answer'",
    ),
    ("human", "{raw_model_output}"),
]
parser_prompt = ChatPromptTemplate.from_messages(messages=_parser_template)
