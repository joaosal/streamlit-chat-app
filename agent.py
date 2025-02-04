import pandas as pd
import requests
from pydantic import Field, BaseModel

from omegaconf import OmegaConf

from vectara_agentic.agent import Agent
from vectara_agentic.tools import ToolsFactory, VectaraToolFactory

initial_prompt = "How can I help you today?"

years = range(2015, 2025)


def get_valid_years() -> list[str]:
    """
    Returns a list of the years for which financial reports are available.
    Always check this before using any other tool.
    """
    return years

def create_assistant_tools(cfg):


    class QueryPublicationsArgs(BaseModel):
        query: str = Field(..., description="The user query, always in the form of a question", examples=["what are the risks reported?", "which drug was use on the and how big was the population?"])        
        
    vec_factory = VectaraToolFactory(vectara_api_key=cfg.api_key,
                                     vectara_customer_id=cfg.customer_id,
                                     vectara_corpus_id=cfg.corpus_id)
    summarizer = 'vectara-summary-ext-24-05-med-omni'
    ask_publications = vec_factory.create_rag_tool(
        tool_name = "ask_publications",
        tool_description = """
        Responds to an user question about a particular result, based on the publications.
        """,
        tool_args_schema = QueryPublicationsArgs,
        reranker = "multilingual_reranker_v1", rerank_k = 100,
        n_sentences_before = 2, n_sentences_after = 2, lambda_val = 0.005,
        summary_num_results = 10,
        vectara_summarizer = summarizer,
        include_citations = True,
    )

    tools_factory = ToolsFactory()
    return (
            [tools_factory.create_tool(tool) for tool in
                [
                    get_valid_years,
                ]
            ] +
            tools_factory.standard_tools() +
            [ask_publications]
    )

def initialize_agent(_cfg, agent_progress_callback=None):
    menarini_bot_instructions = """
    - You are a helpful clinical trial assistant, with expertise in clinical trial test publications, in conversation with a user. 
    - Use the ask_publications tool to answer most questions about the results of clinical trials, risks, and more.
    - Responses from ask_publications are summarized. You don't need to further summarize them.
    """

    agent = Agent(
        tools=create_assistant_tools(_cfg),
        topic="Drug trials publications",
        custom_instructions=menarini_bot_instructions,
        agent_progress_callback=agent_progress_callback,
    )
    agent.report()
    return agent


