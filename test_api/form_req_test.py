import requests
import pandas as pd

# --- 1. Crear una sesión persistente ---
session = requests.Session()

# --- 2. Llamada inicial que genera el JSESSIONID ---
handshake_url = "https://nodia.testing.nodumsoftware.cloud/nweb/METest/"
try:
    resp = session.get(handshake_url, verify=False)
    resp.raise_for_status()
except requests.RequestException as e:
    print(f" Error al obtener sessionID: {e}")
    exit()

# --- Confirmar que la sesión tiene la cookie ---
if 'JSESSIONID' not in session.cookies.get_dict():
    print(" No se recibió un JSESSIONID. Verificá la URL de handshake.")
    exit()

print(f"✅ SessionID obtenido: {session.cookies.get('JSESSIONID')}")

# --- 3. Llamada real al endpoint de datos ---
form_name = "TvntFDirecta"
data_url = f"https://nodia.testing.nodumsoftware.cloud/nweb/METest/registros/data/{form_name}"

params = {
    "field[0][table]": "'tvn_tfdirecta'",
    "field[0][field]": "'nro_trans'",
    "field[1][table]": "'tvn_tfdirecta'",
    "field[1][field]": "'fec_doc'",
    "field[2][table]": "'tvn_tfdirecta'",
    "field[2][field]": "'nro_docum'",
    "field[3][table]": "'tvn_tfdirecta'",
    "field[3][field]": "'cod_tit'",
    "field[4][table]": "'tvn_tfdirecta'",
    "field[4][field]": "'imp_total'",
    "field[5][table]": "'tvn_tfdirecta'",
    "field[5][field]": "'cod_emp'",
    "field[6][table]": "'ct_titulares'",
    "field[6][field]": "'nom_tit'",
    "join[0][sourceTable]": "'tvn_tfdirecta'",
    "join[0][sourceField]": "'cod_tit'",
    "join[0][table]": "'ct_titulares'",
    "join[0][field]": "'cod_tit'",
    "order[0][table]": "'tvn_tfdirecta'",
    "order[0][field]": "'nro_docum'",
    "order[0][desc]": "true",
    "start": 0,
    "pageLength": 1000,
    "includePK": "false",
    "includeNroTrans": "false"
}

try:
    data_resp = session.get(data_url, params=params, verify=False)
    data_resp.raise_for_status()
except requests.RequestException as e:
    print(f"❌ Error al recuperar datos: {e}")
    exit()

# --- Procesar y guardar ---
data_json = data_resp.json().get("data", [])
df = pd.DataFrame(data_json)
df.to_csv("tvntf_directa_sessioned.csv", index=False)
print(" Datos guardados en tvntf_directa_sessioned.csv")
