from langsmith import traceable
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from llm_calc.lib.config import config
from llm_calc.lib import prompts
from langchain_core.runnables import RunnablePassthrough, Runnable
from langchain import hub

llm = config.DEFAULT_LLM
base_prompt = hub.pull("aim/llm-calc-base")
base_model = {"question": RunnablePassthrough()} | base_prompt | llm


@traceable
class BaseAgent:
    def __init__(self, llm, prompt=None):
        util.log("BaseAgent initialized with default config")
        self.llm = llm
        self.prompt = prompt if prompt else prompts.base_prompt
        self.chain = {"human_input": RunnablePassthrough()} | self.prompt | self.llm

    def set_llm(self, llm):
        self.llm = llm

    def set_prompt(self, prompt):
        self.prompt = prompt

    def execute(self, human_input):
        """
        This is preferred.
        :param human_input:
        :return:
        """
        return self.chain.invoke(human_input["human_input"])

    async def aexecute(self, human_input):
        """
        Async version of execute
        :param human_input:
        :return:
        """

        return await self.chain.ainvoke(human_input["human_input"])

    def to_chain(self):
        return self.chain


if __name__ == "__main__":
    print(
        "This file is not meant to be run directly. Please import it in another file."
    )
