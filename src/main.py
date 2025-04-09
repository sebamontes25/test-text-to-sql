import argparse
from langchain_core.messages import HumanMessage
from graph import graph


def main():
    parser = argparse.ArgumentParser(description="Run LangGraph SQL agent")
    parser.add_argument("--question", type=str, required=True,
                        help="Natural language question to answer")
    args = parser.parse_args()

    question = args.question

    graph.invoke({"messages": [HumanMessage(content=question)]})
    print("\n")


if __name__ == "__main__":
    main()
