from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.llms import OpenAI
import openai
import os
from dotenv import load_dotenv, find_dotenv

MODEL = "gpt-4"
_ = load_dotenv("keys.env")
openai.api_key = os.environ['OPENAI_API_KEY']
llm = OpenAI(temperature=0)
tools = load_tools(["openai", "llm-math"], llm=llm)
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
agent.run("Generate a 10 question quiz on the American Revolutionary War")

