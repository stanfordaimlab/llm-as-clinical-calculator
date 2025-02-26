from globals import *

load_dotenv(".env")
from llm_calc.lib.config import config
from langchain import hub
from langchain_openai import ChatOpenAI
import os


from langgraph.prebuilt import create_react_agent

# Get the prompt to use - you can modify this!
prompt = hub.pull("wfh/react-agent-executor")
prompt.pretty_print()

# Choose the LLM that will drive the agent
llm = config.DEFAULT_LLM
planner_llm = config.DEFAULT_LLM
replanner_llm = config.DEFAULT_LLM


# TODO
# REPLACE WITH REAL TOOLS
from typing import Literal
from langchain_core.tools import tool


@tool
def useless_information(city: Literal["nyc", "sf"]):
    """Use this to get useless information."""
    if city == "nyc":
        return "It might be cloudy in nyc"
    elif city == "sf":
        return "It's always sunny in sf"
    else:
        raise AssertionError("Unknown city")


tools = [useless_information]

agent_executor = create_react_agent(llm, tools, messages_modifier=prompt)


from pydantic import BaseModel, Field
from typing import List


class Plan(BaseModel):
    """Plan to follow in future"""

    steps: List[str] = Field(
        description="different steps to follow, should be in sorted order"
    )


from langchain_core.prompts import ChatPromptTemplate

planner_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """For the given objective, come up with a simple step by step plan. \
This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps.
 Make sure that each step has all the information needed - do not skip steps.""",
        ),
        ("placeholder", "{messages}"),
    ]
)

planner = planner_prompt | planner_llm.with_structured_output(Plan)


import operator
from typing import Annotated, List, Tuple, TypedDict


class PlanExecute(TypedDict):
    input: str
    plan: List[str]
    past_steps: Annotated[List[Tuple], operator.add]
    response: str


from typing import Union


class Response(BaseModel):
    """Response to user."""

    response: str


class Act(BaseModel):
    """Action to perform."""

    action: Union[Response, Plan] = Field(
        description="Action to perform. If you want to respond to user, use Response. "
        "If you need to further use tools to get the answer, use Plan."
    )


replanner_prompt = ChatPromptTemplate.from_template(
    """For the given objective, come up with a simple step by step plan. \
This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps. \
The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.

Your objective was this:
{input}

Your original plan was this:
{plan}

You have currently done the follow steps:
{past_steps}

Update your plan accordingly. If no more steps are needed and you can return to the user, then respond with that. Otherwise, fill out the plan. Only add steps to the plan that still NEED to be done. Do not return previously done steps as part of the plan."""
)


replanner = replanner_prompt | replanner_llm.with_structured_output(Act)

from typing import Literal


async def execute_step(state: PlanExecute):
    plan = state["plan"]
    plan_str = "\n".join(f"{i+1}. {step}" for i, step in enumerate(plan))
    task = plan[0]
    task_formatted = f"""For the following plan:
{plan_str}\n\nYou are tasked with executing step {1}, {task}."""
    agent_response = await agent_executor.ainvoke(
        {"messages": [("user", task_formatted)]}
    )
    return {
        "past_steps": [(task, agent_response["messages"][-1].content)],
    }


async def plan_step(state: PlanExecute):
    plan = await planner.ainvoke({"messages": [("user", state["input"])]})
    return {"plan": plan.steps}


async def replan_step(state: PlanExecute):
    output = await replanner.ainvoke(state)
    if isinstance(output.action, Response):
        return {"response": output.action.response}
    else:
        return {"plan": output.action.steps}


def should_end(state: PlanExecute) -> Literal["agent", "__end__"]:
    if "response" in state and state["response"]:
        return "__end__"
    else:
        return "agent"


from langgraph.graph import StateGraph, START

workflow = StateGraph(PlanExecute)

# Add the plan node
workflow.add_node("planner", plan_step)

# Add the execution step
workflow.add_node("agent", execute_step)

# Add a replan node
workflow.add_node("replan", replan_step)

workflow.add_edge(START, "planner")

# From plan we go to agent
workflow.add_edge("planner", "agent")

# From agent, we replan
workflow.add_edge("agent", "replan")

workflow.add_conditional_edges(
    "replan",
    # Next, we pass in the function that will determine which node is called next.
    should_end,
)

# Finally, we compile it!
# This compiles it into a LangChain Runnable,
# meaning you can use it as you would any other runnable
app = workflow.compile()


import asyncio


async def run_agent(config, inputs):
    async for event in app.astream(inputs, config=config):
        for k, v in event.items():
            if k != "__end__":
                print(v)


async def start_and_gather(config, inputs):
    rslt = await asyncio.gather(run_agent(config, inputs))
    return rslt


class ReactAgent:
    def __init__(self):
        self._config = {"recursion_limit": 10}
        self._inputs = {"input": ""}
        os.environ["USER_AGENT"] = "ReactAgent"

    def set_config(self, config):
        self._config = config

    def set_inputs(self, inputs):
        self._inputs = inputs

    def execute(self):
        return asyncio.run(start_and_gather(self._config, self._inputs))


if __name__ == "__main__":
    print(
        "This file is not meant to be run directly. Please import it in another file."
    )

    ra = ReactAgent()
    ra.set_inputs(
        {
            "input": "I'm seeking your expertise to evaluate a patient. This is a 41-year-old woman who has been admitted to the hospital for They are scheduled for a minor ENT surgery. In the past month, they have had the following events: an admission for pneumonia. There have been no other significant medical events in the past one month. The patient has a history of positive lupus anticoagulant and no other venous or clotting disorders. Their mobility is minimal currently, as they are on medical bedrest. Other notable past medical history includes history of COPD. There is no other relevant PMH. Their BMI is 29. Could you help me determine their Caprini VTE risk score?"
        }
    )
    ra.execute()
