# app_agent.py
import streamlit as st
from langchain_core.messages import HumanMessage
from agent_Nodum import graph
import pandas as pd
import io

st.set_page_config(page_title="Nodum ERP AI", layout="centered")
st.title("Nodum ERP AI 🚀")

st.markdown("Pregunta cuántos registros de `TvntFDirecta` querés traer.")

n = st.number_input("Cantidad de registros", min_value=1, max_value=1000, value=5, step=1)

if st.button("Traer datos"):
    with st.spinner("Consultando API..."):
        # El agente espera un HumanMessage con el número
        resp = graph.invoke({"input": str(n)})
        # El agente devolverá primero un razonamiento y luego el JSON
        # Suponemos que el último mensaje es el JSON
        json_str = resp["messages"][-1].content

    st.subheader(f"Primeros {n} registros de TvntFDirecta")
    df = pd.read_json(io.StringIO(json_str))
    st.dataframe(df)

