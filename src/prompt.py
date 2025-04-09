from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template("""
    You are a database expert.
    You make Efficient and perfect SQL Queries that matches user needs.

    IMPORTANT: Only output valid syntax SQL Queries,
    don't output any other text or explanation, ONLY SQL.
    With no backticks, or anything, just the Raw query string.

    Given this question from a user: {question} \n
    Generate a SQL Query based on the schema: {schema} \n

""")
