import os
import requests
from dotenv import load_dotenv
from fastapi import HTTPException 

# Muat variabel dari file .env
load_dotenv()

# Ambil kredensial Cloudflare
ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
DATABASE_ID = os.getenv("CLOUDFLARE_DATABASE_ID")

# Validasi kredensial
if not all([ACCOUNT_ID, API_TOKEN, DATABASE_ID]):
    raise ValueError("Pastikan kredensial Cloudflare (ACCOUNT_ID, API_TOKEN, DATABASE_ID) ada di file .env")

# URL endpoint API Cloudflare D1
D1_API_ENDPOINT = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/d1/database/{DATABASE_ID}/query"

def execute_query(sql_query: str, params: list = None):
    """Menjalankan kueri SQL ke API Cloudflare D1."""
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }
    json_data = {
        "sql": sql_query,
        "params": params if params is not None else [],
    }

    try:
        response = requests.post(D1_API_ENDPOINT, headers=headers, json=json_data)
        response.raise_for_status()
        
        data = response.json()
        if data.get("success"):
            return data.get("results", [])
        else:
            error_details = data.get("errors", [{}])[0].get("message", "Unknown D1 error")
            print(f"Cloudflare D1 Error: {error_details}")
            # PERBAIKAN 2: Jangan return None, lempar error yang jelas
            raise HTTPException(status_code=500, detail=f"Cloudflare D1 Error: {error_details}")

    except requests.exceptions.RequestException as e:
        print(f"Terjadi error HTTP: {e}")
        # PERBAIKAN 3: Jangan return None, lempar error yang jelas
        raise HTTPException(status_code=500, detail=f"HTTP Request Error: {e}")