#all the agents
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os 
from agents import (
    Agent,
    Runner,
    OpenAIChatCompletionsModel,
    set_default_openai_client)

from tools.open_apps import launch_app
from tools.task import handle_task
load_dotenv()


ollama_client = AsyncOpenAI(
    base_url=os.environ.get("OPENAI_BASE_URL"),
    api_key=os.environ.get("OPENAI_API_KEY"),
)
set_default_openai_client(ollama_client)

agent = Agent(
    name="Assistant",
    instructions="You are a system operator.use relevent tools if required,a task list is provided,perform all the task one by one and call the tools relevently",
    model=OpenAIChatCompletionsModel(
        model="qwen3.5:4b",
        openai_client=ollama_client,
    ),
    tools=[launch_app],
)

taskagent = Agent(
    name="task planner",
    instructions='''you are a task planner,make a task list of what to do,store the output in the list of tasks then pass the whole list of taskes to like if user prompts open notepad and browser then task list should be [open notepad,open browser] thats it,no extra items to write clean and short task list of tasks''',
    model=OpenAIChatCompletionsModel(
        model="qwen3.5:4b",
        openai_client=ollama_client,
    )
)

all_agents = [agent,taskagent]
