import os
import requests
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

def execute_query(sql_query: str, params: list = None):
    """Menjalankan kueri SQL ke API Cloudflare D1."""
    
    # Logging untuk debugging
    print(f"=== EXECUTING QUERY ===")
    print(f"SQL: {sql_query}")
    print(f"Params: {params}")
    
    # Mengambil variabel environment
    account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    api_token = os.getenv("CLOUDFLARE_API_TOKEN")
    database_id = os.getenv("CLOUDFLARE_DATABASE_ID")

    if not all([account_id, api_token, database_id]):
        print("ERROR: Missing environment variables")
        raise HTTPException(status_code=500, detail="Environment variables tidak lengkap")

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
        print(f"Response success: {data.get('success')}")
        
        if data.get("success"):
            results = data.get("results", [])
            print(f"Results count: {len(results)}")
            print(f"Results: {results}")
            return results
        else:
            errors = data.get("errors", [])
            print(f"D1 Errors: {errors}")
            error_details = errors[0].get("message", "Unknown D1 error") if errors else "Unknown error"
            raise HTTPException(status_code=500, detail=f"Cloudflare D1 Error: {error_details}")

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        raise HTTPException(status_code=500, detail=f"HTTP Request Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected Error: {e}")