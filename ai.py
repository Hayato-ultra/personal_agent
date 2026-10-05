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
import json
import os
import subprocess

load_dotenv()

ollama_client = AsyncOpenAI(
    base_url=os.environ.get("OPENAI_BASE_URL"),
    api_key=os.environ.get("OPENAI_API_KEY"),
)
# Don't send traces to OpenAI
set_tracing_disabled(True)


set_default_openai_client(ollama_client)

@function_tool
def launch_app(name) :
    '''opens windows application by its name  '''
    with open("tools\\apps.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    app=data["applications"].get(name)
    if app:
        os.startfile(app["path"])
        return "app opened successfully"
    else:
        return "app not found"

agent = Agent(
    name="Assistant",
    instructions="You are a system operator.use relevent tools if required,multiple times tool calling required if there it more than one task like 'open brave and notepad' then open both one by one.",
    model=OpenAIChatCompletionsModel(
        model="qwen3.5:0.8b",
        openai_client=ollama_client,
    ),
    tools=[launch_app],
)

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

    print(result.final_output)
