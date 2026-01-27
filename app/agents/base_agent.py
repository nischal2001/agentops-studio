import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.prompts.system import BASE_SYSTEM_PROMPT

load_dotenv()


class BaseAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="openai/gpt-4o-mini",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", BASE_SYSTEM_PROMPT),
            ("human", "{input}")
        ])

    def run(self, user_input: str):
        chain = self.prompt | self.llm
        return chain.invoke({"input": user_input}).content
