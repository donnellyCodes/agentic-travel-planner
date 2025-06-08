import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

# --- Langchain core imports ---
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_openai_tools_agent

# --- Import Our Custom Tools ---
from tools import get_weather_info, find_hotels, get_daily_spend_estimate

# 1. Load environment variables
load_dotenv()

# --- AGENTIC SETUP ---

# 2. Define the tools the agent can use
tools = [
    get_weather_info,
    find_hotels,
    get_daily_spend_estimate,
]

# 3. Create the LLM instance
# We use a model that is good at tool use, like gpt-4-turbo
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 4. Create prompt template
# This is the "brain" of the agent, guiding its reasoning.
prompt_template = """
You are a specialized Travel Budget assistant. Your goal is to help users plan a trip
by providing a personalized travel plan based on their destination,
budget, and trip duration.

Here is your though process:
1. **Deconstruction the User's Query**: Identify the key information: `destination`, `total_budget`, `duration_days`.
2. **Calculate Accomodation Budget**: A significant portion of the budget will be for hotels.
    Calculate the maximum nightly hotel price. A good rule of thumb is to allocate 40-50% of the
    total budget to accomodation. So `max_hotel_price_per_night = 
    (total_budget * 0.45) / duration_days`.
    You must calculate this value before searching for hotels.
3. **Search for Hotels**: Use the `find_hotels` tools with the `city` and calculated `max_price`.
4. **Estimate Daily Spend**: Use the `get_daily_spend_estimate` tool to
    find out the cost of food and transport.
5. **Get weather Information**: Use thew `get_weather_info` tool for the
    destination.
6. **Synthesize the Final Plan**: Combine all the gathered information
    into a clear, concise, and helpful travel plan.
    Provide the suggested hotels, the estimated daily spend, the total
    estimated cost, and a weather summary.
    If you cannot find hotels withing the budget, state that clearly and suggest alternatives if possible.
    
Begin!

User Query: {input} 
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", prompt_template),
    ("human", "{input}"),
    # The placeholder is where the agent's internal thoughts and tool outputs will go
    ("placeholder", "{agent_scratchpad}"),
])

# 5. Create the Agent
# `create_openai_tools_agent` is a modern way to build agents  that use LLM "tool calling" features
agent = create_openai_tools_agent(llm, tools, prompt)

# 6. Create the Agent Executor
# This runs the agent, invoking tools until a final answer is reached
# `verbose=True` is great for development to see the agent's thought process
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# CLI INTERFACE (for testing)
def run_cli():
    """
    Simple Command Line Interface to interact with the agent.
    """
    print("--- Travel Budget Agentic RAG (CLI) ---")
    print("Type 'exit' to quit.")
    
    while True:
        user_query = input("You: ")
        if user_query.lower() == 'exit':
            break
        
        response = agent_executor.invoke({
            "input": user_query
        })
        
        print("\nAgent:", response['output'], "\n")
        
# FAST API
app = FastAPI(
    title="Travel Budget Agentic RAG API",
    description="An API for generating travel plans using Agentic RAG system."
)

class TravelRequest(BaseModel):
    destination: str
    budget: int
    duration_days: int

@app.post("/plan-trip", summary="Generate a personalized travel plan")
def plan_trip(request: TravelRequest):
    """
    Accepts trip details and returns a generated travel plan.
    """
    # Construct a detailed query for the agent from the structured input
    query = (
        f"I want to go to {request.destination} for {request.duration_days} days "
        f"with a total budget of ${request.budget}."
    )
    
    # Invoke the agent executor
    response = agent_executor.invoke({
        "input": query
    })
    
    return {"plan": response['output']}

# This allows running the CLI by executing `python app.py cli`
if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'cli':
        run_cli()
    else:
        print("To run the CLI: python app.py cli")
        print("To run the API server: uvicorn main:app --reload")
        