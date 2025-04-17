import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPClient, MCPAgent
import os

load_dotenv()

config = {
    "mcpServers": {
        "postgres": {
            "command": "docker",
            "args": [
                "run",
                "-i",
                "--rm",
                "mcp/postgres",
                "postgresql://admin:admin@127.0.0.1:5433/test_text_to_sql"
            ]
        }
    }
}


async def main():
    # Load environment variables
    load_dotenv()

    # Create LLM
    llm = ChatOpenAI(
        model="llama3-70b-8192",
        base_url="https://api.groq.com/openai/v1",
        api_key=os.getenv("GROQ_API_KEY")
    )

    # Create agent with the client
    agent = MCPAgent(llm=llm, client=MCPClient.from_dict(config), max_steps=30)

    # Run the query
    result = await agent.run(
        "how many users are there?"
    )
    print(f"\nResult: {result}")

if __name__ == "__main__":
    asyncio.run(main())
