"""
LEGACY CODE
Kept for learning/reference.
Not used in Patient Journey Orchestration Agent.
"""












# ---------TEXT REPLY BACK APPROACH, this time we have used Langchain tools that are invoking python functions ---------

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from experiments.legacy.langchain_tools import tools

load_dotenv()


class BaseAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="openai/gpt-4o-mini",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )

        self.llm_with_tools = self.llm.bind_tools(tools)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI agent. Use tools when required."),
            ("human", "{input}")
        ])

        self.chain = self.prompt | self.llm_with_tools

        # Map tool name → function
        self.tool_map = {tool.name: tool for tool in tools}

    def run(self, goal: str):
        response = self.chain.invoke({"input": goal})

        # 🔹 CASE 1: Tool was called
        if response.tool_calls:
            outputs = []

            for call in response.tool_calls:
                tool_name = call["name"]
                tool_args = call["args"]

                tool = self.tool_map[tool_name]
                result = tool.invoke(tool_args)

                outputs.append(f"{tool_name} → {result}")

            return "\n".join(outputs)

        # 🔹 CASE 2: Normal text response
        return response.content







#-------------------------------------------TEXT REPLY BACK APPROACH, just like an basic chatbot------------------------



# import os
# from dotenv import load_dotenv
# from langchain_openai import ChatOpenAI
# from langchain_core.prompts import ChatPromptTemplate
# from app.prompts.system import BASE_SYSTEM_PROMPT

# load_dotenv()


# class BaseAgent:
#     def __init__(self):
#         self.llm = ChatOpenAI(
#             model="openai/gpt-4o-mini",
#             temperature=0,
#             api_key=os.getenv("OPENAI_API_KEY"),
#             base_url=os.getenv("OPENAI_BASE_URL"),
#         )

#         self.prompt = ChatPromptTemplate.from_messages([
#             ("system", BASE_SYSTEM_PROMPT),
#             ("human", "{input}")
#         ])

#     def run(self, user_input: str):
#         chain = self.prompt | self.llm
#         return chain.invoke({"input": user_input}).content
