from langchain.agents.output_parsers.tools import ToolAgentAction
from langchain_core.messages import BaseMessage
from typing import List

from globals import *
from pydantic.v1 import BaseModel
from langchain_groq import ChatGroq
from typing import Any
from langchain import hub
from langchain_chroma import Chroma
from langchain_community.document_loaders import UnstructuredHTMLLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import glob
import os
from langchain.tools.retriever import create_retriever_tool

from llm_calc.lib.config import config
from llm_calc.lib import prompts
from operator import itemgetter

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, Runnable


class DocumentationRetriever:
    """
    A class to retrieve documentation from a document store
    """

    k: int = 1
    splitting_enabled: bool = False
    chunk_size: int = 300
    chunk_overlap: int = 200
    document_store: str = os.path.join(config.RAG_DIR, "condensed_html")
    vectorstore: Any = None
    retriever: Any = None
    llm: Any = config.DEFAULT_LLM
    _chain: Any = None

    def initialize_with_llm(
        self, llm: Runnable, prompt: ChatPromptTemplate = None, parser: Any = None
    ) -> bool:
        """Initialize the class with the given llm, prompt and parser
        If not given, default values are used"""
        self.get_retriever_tool()
        rag_prompt = prompts.rag_prompt if prompt is None else prompt
        llm = self.llm if llm is None else llm
        parser = StrOutputParser() if parser is None else parser
        rag_chain = (
            {
                "human_input": itemgetter("human_input"),
                "context": itemgetter("human_input")
                | self.retriever
                | self.format_docs,
            }
            | rag_prompt
            | llm
            | parser
        )
        util.log_mini_task("RAG chain created")
        self._chain = rag_chain
        return True

    @staticmethod
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def set_llm(self, llm):
        """Set the LLM to use"""
        self.llm = llm

    def load_documents(self):
        """Load the documents from the document store"""
        html_files = glob.glob(os.path.join(self.document_store, "*.html"))
        docs = []
        for html_file in html_files:
            loader = UnstructuredHTMLLoader(html_file)
            docs.extend(loader.load())
        if self.splitting_enabled:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
            )
            splits = text_splitter.split_documents(docs)
            self.vectorstore = Chroma.from_documents(
                documents=splits, embedding=OpenAIEmbeddings()
            )
        else:
            splits = docs
            self.vectorstore = Chroma.from_documents(
                documents=splits, embedding=OpenAIEmbeddings()
            )
        util.log_mini_task(
            f"A total of { len(splits) } chunks loaded from { len(html_files) } documents"
        )

    def get_retriever_tool(self):
        """Create a retriever tool, and return it"""
        if self.vectorstore is None:
            self.load_documents()
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": self.k})
        rag_tool = create_retriever_tool(
            self.retriever,
            "information_about_medical_calculator",
            "Returns information about a specific medical calculator from a verified source.",
        )
        return rag_tool

    @staticmethod
    def format_to_tool_message(
        agent_action: ToolAgentAction,
        observation: dict,
    ) -> List[BaseMessage]:
        """
        Format the output of the CodeInterpreter tool to be returned as a ToolMessage.
        """
        import json
        from langchain_core.messages import ToolMessage

        new_messages = list(agent_action.message_log)

        # # TODO: Returns the "result" (returned value from cell) generally as list of Class Result
        # if isinstance(observation["results"], list):
        #     observation["results"] = [obs.text for obs in observation["results"]]
        # else:
        #     observation["results"] = observation["results"].text

        the_observation = {"Information": observation}

        content = json.dumps(
            # {k: v for k, v in observation.items()}, indent=2
            {k: v for k, v in the_observation.items()},
            indent=2,
        )

        new_messages.append(
            ToolMessage(content=content, tool_call_id=agent_action.tool_call_id)
        )
        return new_messages

    def to_chain(self):
        """Returns a chain using the RAG tool using the prompt from the hub. default prompt is
        aim/llm-calc-rag and default llm is config.DEFAULT_LLM"""
        return self._chain

    def execute(self, human_input):
        return self._chain.invoke(human_input)


if __name__ == "__main__":
    print(
        "This file is not meant to be run directly. Please import it in another file."
    )
