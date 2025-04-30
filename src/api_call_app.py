from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()


@app.get("/")
async def home():
    return {"message": "Welcome to Nodum Test API"}


@app.post("/nodum_test")
async def nodum_test(request: Request):
    data = await request.json()
    query = data.get("query", "No query received")
    question = data.get("Question", "No question received")
    thoughts = data.get("thoughts", "No thoughts received")
    result = data.get("result", "No result received")
    metadata = data.get("metadata", "No metadata received")

    print(f"Received Question: {question}")
    print(f"Received Thoughts: {thoughts}")
    print(f"Received SQL Query: {query}")
    print(f"Received Result: {result}")
    print(f"Received Metadata: {metadata}")

    return JSONResponse(content={
        "message": "Data received successfully!",
        "received_query": query,
        "received_question": question,
        "received_thoughts": thoughts,
        "result": result,
        "received_metadata": metadata
    })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
