import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import bigquery
from pydantic import BaseModel
from passlib.context import CryptContext

# 1. Setup and Config
app = FastAPI(title="Uncle Joe's Coffee API")

# Configure CORS for your frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with your frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize BigQuery Client
# Cloud Run will use the service account automatically if permissions are set
client = bigquery.Client()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Set your BigQuery IDs here
PROJECT_ID = "uncle-joes-coffee-club"
DATASET_ID = "uncle_joes"

# 2. Pydantic Models for Response Validation
class LoginRequest(BaseModel):
    email: str
    password: str

# 3. Helper Function for Queries
def run_query(query: str, job_config=None):
    try:
        query_job = client.query(query, job_config=job_config)
        return [dict(row) for row in query_job]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- ENDPOINTS ---

@app.get("/menu")
def get_menu():
    # Matches Image 1 schema
    query = f"SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.menu_items`"
    return run_query(query)

@app.get("/menu/search")
def search_menu(item_name: str):
    # TRIM(name) ensures that accidental spaces in BigQuery don't break the search
    query = f"""
        SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.menu_items` 
        WHERE LOWER(TRIM(name)) LIKE @name
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("name", "STRING", f"%{item_name.lower()}%")]
    )
    return run_query(query, job_config)

@app.get("/menu/categories")
def get_menu_categories():
    # Returns a unique list of categories for the navigation UI
    query = f"SELECT DISTINCT category FROM `{PROJECT_ID}.{DATASET_ID}.menu_items` ORDER BY category"
    return run_query(query)

@app.get("/menu/{item_id}")
def get_menu_item(item_id: str):
    # Matches Image 1: 'id' is a STRING
    query = f"SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.menu_items` WHERE id = @item_id"
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("item_id", "STRING", item_id)]
    )
    results = run_query(query, job_config)
    if not results:
        raise HTTPException(status_code=404, detail="Item not found")
    return results[0]



@app.get("/menu/search")
def search_menu(item_name: str):
    # TRIM(name) ensures that accidental spaces in BigQuery don't break the search
    query = f"""
        SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.menu_items` 
        WHERE LOWER(TRIM(name)) LIKE @name
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("name", "STRING", f"%{item_name.lower()}%")]
    )
    return run_query(query, job_config)

@app.get("/locations")
def get_locations():
    query = f"SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.locations` WHERE open_for_business = True"
    return run_query(query)

@app.get("/locations/{location_id}")
def get_location(location_id: str):
    query = f"SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.locations` WHERE id = @id"
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("id", "STRING", location_id)]
    )
    results = run_query(query, job_config)
    if not results:
        raise HTTPException(status_code=404, detail="Location not found")
    return results[0]

@app.get("/locations/filter/{state}")
def get_locations_by_state(state: str):
    # Matches Image 4: Field name is 'state'
    query = f"SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.locations` WHERE state = @state"
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("state", "STRING", state.upper())]
    )
    return run_query(query, job_config)

@app.post("/login")
def login(auth: LoginRequest):
    # Now using the clean 'email' and 'password' columns
    query = f"SELECT email, password FROM `{PROJECT_ID}.{DATASET_ID}.members` WHERE email = @email"
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("email", "STRING", auth.email)]
    )
    results = run_query(query, job_config)
    
    if not results or not pwd_context.verify(auth.password, results[0]['password']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    return {"message": "Login successful", "email": auth.email}

@app.get("/members/{member_id}/orders")
def get_member_orders(member_id: str):
    query = f"""
        SELECT o.order_id, o.order_date, o.order_total, i.item_name, i.quantity, i.price
        FROM `{PROJECT_ID}.{DATASET_ID}.orders` o
        JOIN `{PROJECT_ID}.{DATASET_ID}.order_items` i ON o.order_id = i.order_id
        WHERE o.member_id = @member_id
        ORDER BY o.order_date DESC
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("member_id", "STRING", member_id)]
    )
    return run_query(query, job_config)

@app.get("/members/{member_id}/points")
def get_member_points(member_id: str):
    # This now joins orders to the members table using your new 'id' column
    query = f"""
        SELECT SUM(order_total) as total_spent 
        FROM `{PROJECT_ID}.{DATASET_ID}.orders` 
        WHERE member_id = @member_id
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("member_id", "STRING", member_id)]
    )
    results = run_query(query, job_config)
    
    points = int(results[0]['total_spent'] or 0)
    return {"member_id": member_id, "loyalty_points": points}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
