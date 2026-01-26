from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.prompts.system import BASE_SYSTEM_PROMPT

class BaseAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", BASE_SYSTEM_PROMPT),
            ("human", "{input}")
        ])

    def run(self, user_input: str):
        chain = self.prompt | self.llm
        return chain.invoke({"input": user_input}).content
