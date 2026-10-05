from openai import AsyncOpenAI
from dotenv import load_dotenv
import os 
from agents import (
    Agent,
    Runner,
    OpenAIChatCompletionsModel,
    set_default_openai_client,
    set_tracing_disabled,
    function_tool
)
from memory.memory import ProceduralMemory
from customAgents.agents import taskagent,agent
# Don't send traces to OpenAI
set_tracing_disabled(True)





def contexts(query):
    context = {
    "user_request": query ,
    "actions": [],
    "completed": [],
    "failed": [],
    "results": []
    }    
    
while True:
    query = input("enter question:")
    
    result = Runner.run_sync(
        agent,query
    )
    tasks = result.final_output
    print(tasks)
    works = Runner.run_sync(
        agent,tasks
    )

    print(works.final_output)
