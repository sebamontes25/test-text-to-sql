# agent_Nodum.py

import os
import io
import requests
import pandas as pd
from http.cookies import SimpleCookie
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import Tool, initialize_agent, AgentType

load_dotenv()

# ————————————————————————
# Configuración de la API Nodum
# ————————————————————————
LOGIN_URL   = "https://nodia.testing.nodumsoftware.cloud:444/nweb/nodia/desk/n_security_check"
DATA_URL    = "https://nodia.testing.nodumsoftware.cloud:444/nweb/nodia/registros/data"
COOKIE_FILE = "session_cookie.txt"
session     = requests.Session()

def login_if_needed():
    """Verifica si hay una cookie de sesión guardada en un archivo. Si la hay,
    la carga en la sesión actual y devuelve. Si no la hay, intenta hacer un
    login manual y, si tiene éxito, guarda la cookie en el archivo para usarla
    en solicitudes futuras."""
    if os.path.exists(COOKIE_FILE):
        with open(COOKIE_FILE, "r") as f:
            session.cookies.set("JSESSIONID", f.read().strip(),
                                domain="nodia.testing.nodumsoftware.cloud")
        return
    resp = session.post(
        LOGIN_URL,
        data={"j_username": os.getenv("NODUM_USER"), "j_password": os.getenv("NODUM_PASS")},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        verify=False, allow_redirects=False
    )
    cookie = SimpleCookie(resp.headers.get("Set-Cookie", ""))
    if "JSESSIONID" in cookie:
        js = cookie["JSESSIONID"].value
        session.cookies.set("JSESSIONID", js,
                            domain="nodia.testing.nodumsoftware.cloud")
        with open(COOKIE_FILE, "w") as f:
            f.write(js)

def fetch_tvn_df(limit: int = 1000) -> pd.DataFrame:
    """
    Trae hasta `limit` filas y devuelve un DataFrame con columnas normalizadas.
    
    La normalización de columnas consiste en reemplazar los puntos ('.') por
    guiones bajos ('_') en los nombres de columna.
    """
    login_if_needed()
    # construimos los parámetros de la consulta
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
    try:
        # enviamos la solicitud
        r = session.get(
            url, params=params,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "https://nodia.testing.nodumsoftware.cloud:444/nweb/nodia/desk/"
            },
            verify=False
        )
        # verificamos si la respuesta es correcta
        if r.status_code != 200:
            return pd.DataFrame()
        # parseamos la respuesta en un DataFrame
        data = r.json().get("data", [])
        df = pd.DataFrame(data)
        # normalizamos las columnas
        df.columns = [col.replace('.', '_') for col in df.columns]
        return df
    except Exception as e:
        print(f"Error al traer los datos: {e}")
        return pd.DataFrame()

# variable global para almacenar el último JSON
last_json: str = "[]"


# ————————————————————————
# Tool 1: fetch
# ————————————————————————
def run_fetch_tool(text: str) -> str:
    """
    USO:
      fetch(N)
    donde N es un entero. Devuelve un JSON con las primeras N filas.
    """
    global last_json
    cleaned = text.strip().strip("'\"")
    try:
        n = int(cleaned)
    except ValueError:
        return "❌ Formato inválido; pasa solo un número (p.ej. 100)."
    df = fetch_tvn_df(n)
    last_json = df.to_json(orient="records")
    return last_json

fetch_tool = Tool(
    name="fetch",
    func=run_fetch_tool,
    description=(
        "USO:\n"
        "  fetch(N)\n"
        "Obtiene las primeras N filas de TvntFDirecta como JSON,\n"
        "con columnas normalizadas ('.' → '_')."
    )
)


# ————————————————————————
# Tool 2: filter
# ————————————————————————
def run_filter_tool(expr: str) -> str:
    """
    USO:
      filter(EXPR)
    expr es una pandas.DataFrame.query expression sobre el último JSON.
    Ejemplo: filter(\"fec_doc.str.startswith('2025-04')\")
    """
    global last_json
    try:
        df = pd.read_json(io.StringIO(last_json), orient="records")
    except ValueError:
        return "❌ No hay datos: usa fetch(N) primero."
    try:
        filtered = df.query(expr)
    except Exception as e:
        return f"❌ Error en filtro: {e}"
    last_json = filtered.to_json(orient="records")
    return last_json

filter_tool = Tool(
    name="filter",
    func=run_filter_tool,
    description=(
        "USO:\n"
        "  filter(EXPR)\n"
        "Aplica EXPR con pandas.DataFrame.query al último JSON."
    )
)


# ————————————————————————
# Tool 3: save
# ————————————————————————
def run_save_tool(text: str) -> str:
    """
    USO:
      save(PATH.csv)
    Guarda el último JSON en un archivo CSV.
    """
    global last_json
    path = text.strip()
    try:
        df = pd.read_json(io.StringIO(last_json), orient="records")
    except ValueError:
        return "❌ No hay datos: usa fetch(N) primero."
    try:
        df.to_csv(path, index=False)
    except Exception as e:
        return f"❌ Error al guardar CSV: {e}"
    return f"✅ Guardado en {path}"

save_tool = Tool(
    name="save",
    func=run_save_tool,
    description="USO: save(path.csv) — Guarda el último JSON en CSV."
)


# ————————————————————————
# Inicialización del agente
# ————————————————————————
system_prompt = """
Eres un agente que SOLO usa herramientas.  

Herramientas:
- fetch(N): trae N filas como JSON (columnas con '_')
- filter(EXPR): filtra el JSON actual con pandas.query
- save(PATH): guarda el JSON actual en CSV

primero dame un plan de accion y tools que vas a usar para hacerlo y espera validacion de plan por parte del usuario.
Luego podes usar este flujo como referencia:

Flujo:
1) fetch  
2) filter (opcional)  
3) save  

Responde únicamente:
Action: tool_name
Action Input: ...
"""

llm = ChatOpenAI(
    model="llama3-70b-8192",
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

graph = initialize_agent(
    tools=[fetch_tool, filter_tool, save_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    system_message=system_prompt,
    verbose=True,
    handle_parsing_errors=True
)


# ————————————————————————
# Modo CLI
# ————————————————————————
if __name__ == "__main__":
    print("🤖 Nodum ERP AI — escribe tu comando (o 'exit'):")
    while True:
        text = input(">> ")
        if text.lower() in ("exit", "quit"):
            break
        try:
            print(graph.run(text))
        except Exception as e:
            print("⚠️ Error:", e)
