import os
import requests
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

def execute_query(sql_query: str, params: list = None):
    """Menjalankan kueri SQL ke API Cloudflare D1."""
    
    # ==================== TES BARU ====================
    # Cetak status variabel lingkungan yang dilihat oleh Vercel
    # Ini akan muncul di log Vercel (Tab "Logs" di dasbor proyek Anda)
    print("--- MEMERIKSA ENVIRONMENT VARIABLES ---")
    account_id_status = 'Ada' if os.getenv('CLOUDFLARE_ACCOUNT_ID') else 'Tidak Ada / Kosong'
    api_token_status = 'Ada' if os.getenv('CLOUDFLARE_API_TOKEN') else 'Tidak Ada / Kosong'
    database_id_status = 'Ada' if os.getenv('CLOUDFLARE_DATABASE_ID') else 'Tidak Ada / Kosong'
    
    print(f"Untuk kueri: {sql_query}")
    print(f"CLOUDFLARE_ACCOUNT_ID: {account_id_status}")
    print(f"CLOUDFLARE_API_TOKEN: {api_token_status}")
    print(f"CLOUDFLARE_DATABASE_ID: {database_id_status}")
    print("------------------------------------")
    # ================================================

    # Mengambil variabel di dalam fungsi untuk memastikan nilainya yang terbaru
    account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    api_token = os.getenv("CLOUDFLARE_API_TOKEN")
    database_id = os.getenv("CLOUDFLARE_DATABASE_ID")

    # Validasi dipindahkan ke sini agar kita bisa melihat lognya terlebih dahulu
    if not all([account_id, api_token, database_id]):
        # Jika salah satu variabel kosong, kita langsung hentikan dan beri tahu
        raise HTTPException(status_code=500, detail="Satu atau lebih Environment Variables Cloudflare tidak diatur dengan benar di Vercel.")

    endpoint = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/d1/database/{database_id}/query"
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }
    json_data = {
        "sql": sql_query,
        "params": params if params is not None else [],
    }

    try:
        response = requests.post(endpoint, headers=headers, json=json_data)
        response.raise_for_status()
        
        data = response.json()
        if data.get("success"):
            return data.get("results", [])
        else:
            error_details = data.get("errors", [{}])[0].get("message", "Unknown D1 error")
            raise HTTPException(status_code=500, detail=f"Cloudflare D1 Error: {error_details}")

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"HTTP Request Error: {e}")
