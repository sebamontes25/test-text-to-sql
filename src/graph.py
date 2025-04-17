from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated
from db_manager import DatabaseManager
from langchain_openai import ChatOpenAI
from prompt import prompt
import os
from langchain_core.messages import AIMessage


class GraphState(TypedDict):
    messages: Annotated[list, add_messages]


llm = ChatOpenAI(
    model="llama3-70b-8192",
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

db = DatabaseManager()


def generate_sql_query(state: GraphState):
    chain = prompt | llm
    question = state["messages"][-1].content
    sql = chain.invoke({"question": question, "schema": db.get_schema()})
    content = sql.content
    print("====== \n" + "SQL: " + content)

    return {"messages":
            state["messages"] + [{"role": "assistant", "content": content}]}


def run_query(state: GraphState):
    query = state["messages"][-1].content
    df = db.raw_query_invoke(query)
    json_data = df.to_json(orient="records")

    print("====== \n" + "RESULT: " + json_data)

    return {"messages": state["messages"] + [AIMessage(content=json_data)]}


builder = StateGraph(GraphState)

builder.add_node("generate_sql_query", generate_sql_query)
builder.add_node("run_query", run_query)

builder.add_edge(START, "generate_sql_query")
builder.add_edge("generate_sql_query", "run_query")
builder.add_edge("run_query", END)

graph = builder.compile()
