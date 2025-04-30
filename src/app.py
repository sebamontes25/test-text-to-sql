import streamlit as st
from langchain_core.messages import HumanMessage
from graph import graph
import pandas as pd
import io

# st.title("Text-to-SQL with Marvik & Nodum")
st.title("Nodum ERP 🚀 - Text-to-SQL")

question = st.text_area(
    "¿Qué quieres buscar?",
    placeholder="e.g. ¿Cuántos productos fueron vendidos la semana pasada?",
    height=100
)

if st.button("Consultar") and question:
    with st.spinner("Pensando..."):
        result = graph.invoke({"messages": [HumanMessage(content=question)]})
        print(result)
        sql = result["messages"][-2].content
        answer_raw = result["messages"][-1].content

        st.subheader("SQL Generado")
        st.code(sql, language="sql")
        st.subheader("Respuesta")
        # df = pd.read_json(answer_raw)
        df = pd.read_json(io.StringIO(answer_raw))
        st.table(df)
