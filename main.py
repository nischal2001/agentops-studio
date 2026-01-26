from app.agents.base_agent import BaseAgent

agent = BaseAgent()

while True:
    goal = input("\n🎯 Goal > ")
    if goal.lower() == "exit":
        break
    response = agent.run(goal)
    print("\n🤖 Agent Output:\n", response)
