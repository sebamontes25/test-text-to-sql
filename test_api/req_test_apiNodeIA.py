import os
import requests
import pandas as pd
from http.cookies import SimpleCookie
from dotenv import load_dotenv
import os
from urllib.parse import urlencode

load_dotenv()

# --- Configuración ---
LOGIN_URL = "https://nodia.testing.nodumsoftware.cloud:444/nweb/nodia/desk/n_security_check"
DATA_URL = "https://nodia.testing.nodumsoftware.cloud:444/nweb/nodia/registros/data"
# DATA_URL = "https://nodia.testing.nodumsoftware.cloud:444/nweb/nodia/registros/data/EXPIRIENCE/Comercial/REPORTES/TvntFDirecta"
COOKIE_FILE = "session_cookie.txt"
username = os.getenv("NODUM_USER")
password = os.getenv("NODUM_PASS")

session = requests.Session()

# --- Intentar cargar cookie desde archivo ---
def load_cookie():
    if os.path.exists(COOKIE_FILE):
        with open(COOKIE_FILE, "r") as f:
            cookie_value = f.read().strip()
            session.cookies.set("JSESSIONID", cookie_value, domain="nodia.testing.nodumsoftware.cloud")
            print(f"🔄 Usando cookie previa: {cookie_value}")
            return True
    return False

# --- Intentar login manual si no hay cookie válida ---
def login_and_save_cookie():
    print("🔐 Haciendo login...")
    payload = {
        "j_username": username,
        "j_password": password
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Python Script"
    }

    resp = session.post(LOGIN_URL, data=payload, headers=headers, verify=False, allow_redirects=False)
    set_cookie = resp.headers.get("Set-Cookie", "")
    cookie = SimpleCookie()
    cookie.load(set_cookie)

    if "JSESSIONID" in cookie:
        jsessionid = cookie["JSESSIONID"].value
        session.cookies.set("JSESSIONID", jsessionid, domain="nodia.testing.nodumsoftware.cloud")
        with open(COOKIE_FILE, "w") as f:
            f.write(jsessionid)
        print(f"✅ Login exitoso. Cookie guardada: {jsessionid}")
        return True
    else:
        print("❌ Login fallido o cookie no recibida")
        return False

# --- Lógica principal para obtener datos ---
def get_data():
    form = "TvntFDirecta"
    print("📥 Recuperando datos...")
    # params = {
    #     "field[0][table]": "'tvn_tfdirecta'",
    #     "field[0][field]": "'nro_trans'",
    #     "field[1][table]": "'tvn_tfdirecta'",
    #     "field[1][field]": "'fec_doc'",
    #     "field[2][table]": "'tvn_tfdirecta'",
    #     "field[2][field]": "'nro_docum'",
    #     "field[3][table]": "'tvn_tfdirecta'",
    #     "field[3][field]": "'cod_tit'",
    #     "field[4][table]": "'tvn_tfdirecta'",
    #     "field[4][field]": "'imp_total'",
    #     "field[5][table]": "'tvn_tfdirecta'",
    #     "field[5][field]": "'cod_emp'",
    #     "field[6][table]": "'ct_titulares'",
    #     "field[6][field]": "'nom_tit'",
    #     "join[0][sourceTable]": "'tvn_tfdirecta'",
    #     "join[0][sourceField]": "'cod_tit'",
    #     "join[0][table]": "'ct_titulares'",
    #     "join[0][field]": "'cod_tit'",
    #     "order[0][table]": "'tvn_tfdirecta'",
    #     "order[0][field]": "'nro_docum'",
    #     "order[0][desc]": "true",
    #     "start": "0",
    #     "pageLength": "5",
    #     "includePK": "false",
    #     # "includeNroTrans": "false"
    # }
    params = {
        "field[0][table]": "'tvn_tfdirecta'",
        "field[0][field]": "'nro_trans'",
        "field[1][table]": "'cpt_facturas'",
        "field[1][field]": "'fec_doc'",
        "field[2][table]": "'cpt_facturas'",
        "field[2][field]": "'cod_emp'",
        "start": "0",
        "pageLength": "5",
        "includePK": "false",
        # "includeNroTrans": "false"
    }
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://nodia.testing.nodumsoftware.cloud:444/nweb/nodia/desk/",
        }
        print("📤 Enviando:", params)

        URL_consulta = f"{DATA_URL}/{form}"
        response = session.get(URL_consulta, params=params, headers=headers, verify=False)
        print("🌐 URL:", URL_consulta)
        print("🧾 Payload codificado:", urlencode(params))
    except requests.RequestException as e:
        print(f"❌ Error de red: {e}")
        return False

    # --- Verificar si la sesión está expirada ---
    content_type = response.headers.get("Content-Type", "")
    if "text/html" in content_type and "login" in response.text.lower():
        print("⚠️ La sesión expiró. Borrando cookie...")
        if os.path.exists(COOKIE_FILE):
            os.remove(COOKIE_FILE)
        return False

    if response.status_code != 200:
        print(f"❌ Error al recuperar datos: {response.status_code}")
        print(response.text[:500])
        return False

    # --- Procesar respuesta ---
    data = response.json().get("data", [])
    print("📦 Datos recibidos:", len(data))
    print(data)
    df = pd.DataFrame(data)
    df.to_csv("tvntf_directa_result.csv", index=False)
    print("✅ Datos guardados en tvntf_directa_result.csv")
    return True

# --- Ejecución ---
if not load_cookie():
    if not login_and_save_cookie():
        exit()

if not get_data():
    print("💥 Volvé a ejecutar el script para reintentar con login nuevo.")
