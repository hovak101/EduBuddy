from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.llms import OpenAI
from langchain.tools.python.tool import PythonREPLTool
from langchain.utilities import SerpAPIWrapper

import os
from dotenv import load_dotenv, find_dotenv
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
load_dotenv(find_dotenv())
llm = OpenAI(temperature=0)
tools = load_tools(["wolfram-alpha", "serpapi"], llm=llm)
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)


def retMulChoice(text):
    val = (agent.run(text))
    return(val)
    








 