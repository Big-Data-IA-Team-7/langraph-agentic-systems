from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

from langchain_core.agents import AgentAction
from state_schema import AgentState
from config import OPENAI_API_KEY
from langgraph_tools import rag_search, fetch_arxiv, web_search, final_answer
from utilities import create_scratchpad, build_report

system_prompt = """
You are the supervisor, the great AI tool manager.
Given the user's query you must orchestrate a path where the query is first
sent to a rag_search tool.

If relevant information is found in the rag_search tool then you must navigate 
to the web_search tool. Upon returning from the web_search tool you must send 
the query to the fetch_arxiv tool to retrieve the content from relevant arxiv
pages. You are allowed to reuse tools to get additional information if necessary.

If you see that a tool has been used (in the scratchpad) with a particular
query, do NOT use that same tool with the same query again. Also, do NOT use
any tool more than twice (ie, if the tool appears in the scratchpad twice, do
not use it again).

You should aim to collect information from a diverse range of sources before
providing the answer to the user. Once you have collected plenty of information
to answer the user's question (stored in the scratchpad) use the final_answer
tool.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    ("assistant", "scratchpad: {scratchpad}"),
])

llm = ChatOpenAI(
    model="gpt-4o",
    openai_api_key=OPENAI_API_KEY,
    temperature=0
)

tools=[
    rag_search,
    web_search,
    fetch_arxiv,
    final_answer
]

oracle = (
    {
        "input": lambda x: x["input"],
        "chat_history": lambda x: x["chat_history"],
        "scratchpad": lambda x: create_scratchpad(
            intermediate_steps=x["intermediate_steps"]
        ),
    }
    | prompt
    | llm.bind_tools(tools, tool_choice="any")
)

def run_oracle(state: list):
    print("run_oracle")
    print(f"intermediate_steps: {state['intermediate_steps']}")
    out = oracle.invoke(state)
    print(out)
    tool_name = out.tool_calls[0]["name"]
    tool_args = out.tool_calls[0]["args"]
    action_out = AgentAction(
        tool=tool_name,
        tool_input=tool_args,
        log="TBD"
    )
    return {
        "intermediate_steps": [action_out]
    }

def router(state: list):
    # return the tool name to use
    if isinstance(state["intermediate_steps"], list):
        return state["intermediate_steps"][-1].tool
    else:
        # if we output bad format go to final answer
        print("Router invalid format")
        return "final_answer"

def rag_router(state: list):
    if state["intermediate_steps"][-1].log == "I don't know.":
        return END
    else:
        return "oracle"
    
tool_str_to_func = {
    "rag_search": rag_search,
    "fetch_arxiv": fetch_arxiv,
    "web_search": web_search,
    "final_answer": final_answer
}

def run_tool(state: list):
    # use this as helper function so we repeat less code
    tool_name = state["intermediate_steps"][-1].tool
    tool_args = state["intermediate_steps"][-1].tool_input
    print(f"{tool_name}.invoke(input={tool_args})")
    # run tool
    out = tool_str_to_func[tool_name].invoke(input=tool_args)
    action_out = AgentAction(
        tool=tool_name,
        tool_input=tool_args,
        log=str(out)
    )
    return {"intermediate_steps": [action_out]}

graph = StateGraph(AgentState)

graph.add_node("oracle", run_oracle)
graph.add_node("rag_search", run_tool)
graph.add_node("fetch_arxiv", run_tool)
graph.add_node("web_search", run_tool)
graph.add_node("final_answer", run_tool)

graph.set_entry_point("oracle")

graph.add_conditional_edges(
    source="oracle",  # where in graph to start
    path=router,  # function to determine which node is called
)

graph.add_conditional_edges(
    source="rag_search",
    path=rag_router,
)

for tool_obj in tools:
    if tool_obj.name not in ["final_answer", "rag_search"]:
        graph.add_edge(tool_obj.name, "oracle")

graph.add_edge("final_answer", END)

runnable = graph.compile()

out = runnable.invoke({
    "input": "tell me something interesting about hedging for canadian investors",
    "chat_history": [],
})

print(build_report(
    output=out["intermediate_steps"][-1].tool_input
))
