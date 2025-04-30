# agent_Nodum.py
import os
import requests
import pandas as pd
from http.cookies import SimpleCookie
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import Tool, initialize_agent
from langchain.llms import OpenAI

load_dotenv()

LOGIN_URL   = "https://nodia.testing.nodumsoftware.cloud:444/nweb/nodia/desk/n_security_check"
DATA_URL    = "https://nodia.testing.nodumsoftware.cloud:444/nweb/nodia/registros/data"
COOKIE_FILE = "session_cookie.txt"
session     = requests.Session()

def login_if_needed():
    if os.path.exists(COOKIE_FILE):
        with open(COOKIE_FILE, "r") as f:
            session.cookies.set("JSESSIONID", f.read().strip(),
                                domain="nodia.testing.nodumsoftware.cloud")
        return
    resp = session.post(
        LOGIN_URL,
        data={"j_username":os.getenv("NODUM_USER"), "j_password":os.getenv("NODUM_PASS")},
        headers={"Content-Type":"application/x-www-form-urlencoded"},
        verify=False, allow_redirects=False
    )
    cookie = SimpleCookie(resp.headers.get("Set-Cookie",""))
    if "JSESSIONID" in cookie:
        js = cookie["JSESSIONID"].value
        session.cookies.set("JSESSIONID", js,
                            domain="nodia.testing.nodumsoftware.cloud")
        with open(COOKIE_FILE, "w") as f:
            f.write(js)

def fetch_tvn(limit: int = 5) -> str:
    """Devuelve las primeras `limit` filas en JSON."""
    login_if_needed()
    params = {
        "field[0][table]": "'tvn_tfdirecta'",
        "field[0][field]": "'nro_trans'",
        "field[1][table]": "'cpt_facturas'",
        "field[1][field]": "'fec_doc'",
        "field[2][table]": "'cpt_facturas'",
        "field[2][field]": "'cod_emp'",
        "start": "0",
        "pageLength": str(limit),
        "includePK": "false"
    }
    url = f"{DATA_URL}/TvntFDirecta"
    r = session.get(url, params=params, headers={
        "User-Agent":"Mozilla/5.0",
        "Accept":"application/json, text/javascript, */*; q=0.01",
        "X-Requested-With":"XMLHttpRequest",
        "Referer":"https://nodia.testing.nodumsoftware.cloud:444/nweb/nodia/desk/"
    }, verify=False)
    data = r.json().get("data", [])
    # lo devolvemos como JSON de string
    return pd.DataFrame(data).to_json(orient="records")

# Definimos el Tool
tvn_tool = Tool(
    name="tvn_data_fetcher",
    func=lambda text: fetch_tvn(int(text)),
    description="Recibe un entero N y devuelve las primeras N filas de TvntFDirecta en JSON."
)

# Creamos el agente
llm = ChatOpenAI(
    model="llama3-70b-8192",
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

graph = initialize_agent(
    tools=[tvn_tool],
    llm=llm,
    agent="zero-shot-react-description",
    verbose=False
)

