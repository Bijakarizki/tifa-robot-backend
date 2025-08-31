import os
import requests
from fastapi import HTTPException

# Tidak menggunakan dotenv dulu untuk menghindari masalah import
# load_dotenv()

def execute_query(sql_query: str, params: list = None):
    """Menjalankan kueri SQL ke API Cloudflare D1."""
    
    try:
        print(f"=== EXECUTING QUERY ===")
        print(f"SQL: {sql_query}")
        print(f"Params: {params}")
        
        # Mengambil variabel environment langsung dari os.environ
        account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
        api_token = os.environ.get("CLOUDFLARE_API_TOKEN") 
        database_id = os.environ.get("CLOUDFLARE_DATABASE_ID")
        
        print(f"Environment check:")
        print(f"- Account ID: {'OK' if account_id else 'MISSING'}")
        print(f"- API Token: {'OK' if api_token else 'MISSING'}")
        print(f"- Database ID: {'OK' if database_id else 'MISSING'}")

        if not account_id:
            raise HTTPException(status_code=500, detail="CLOUDFLARE_ACCOUNT_ID not set")
        if not api_token:
            raise HTTPException(status_code=500, detail="CLOUDFLARE_API_TOKEN not set")  
        if not database_id:
            raise HTTPException(status_code=500, detail="CLOUDFLARE_DATABASE_ID not set")

        endpoint = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/d1/database/{database_id}/query"
        print(f"Endpoint: {endpoint}")
        
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }
        
        json_data = {
            "sql": sql_query,
            "params": params if params is not None else [],
        }
        
        print(f"Request data: {json_data}")

        response = requests.post(endpoint, headers=headers, json=json_data, timeout=30)
        
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        
        response.raise_for_status()
        
        data = response.json()
        print(f"Parsed response: {data}")
        
        if data.get("success"):
            results = data.get("results", [])
            print(f"Query successful, results count: {len(results)}")
            return results
        else:
            errors = data.get("errors", [])
            print(f"Query failed, errors: {errors}")
            error_msg = errors[0].get("message", "Unknown D1 error") if errors else "Unknown error"
            raise HTTPException(status_code=500, detail=f"D1 Error: {error_msg}")

    except requests.exceptions.Timeout:
        print("Request timeout")
        raise HTTPException(status_code=500, detail="Database request timeout")
    except requests.exceptions.RequestException as e:
        print(f"Request exception: {e}")
        raise HTTPException(status_code=500, detail=f"Request Error: {str(e)}")
    except HTTPException:
        raise  # Re-raise HTTPException
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected Error: {str(e)}")