from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from zoho_service import (
    generate_auth_url, exchange_code_for_token,
    get_access_token, get_leads, create_lead
)
from storage_service import store_refresh_token, get_refresh_token

app = FastAPI()

@app.get("/")
def root():
    return {"status": "Zoho Multi-Account API Running"}

@app.get("/zoho/generate-auth-url")
def auth_url(user_id: str):
    url = generate_auth_url(user_id)
    return {"auth_url": url}

@app.get("/zoho/callback")
def oauth_callback(code: str, state: str):
    refresh_token = exchange_code_for_token(code)
    store_refresh_token(state, refresh_token)
    return RedirectResponse(url="https://teams.microsoft.com") 

@app.get("/zoho/get_leads")
def get_user_leads(user_id: str):
    refresh_token = get_refresh_token(user_id)
    if not refresh_token:
        raise HTTPException(status_code=400, detail="User not authorized.")
    access_token = get_access_token(refresh_token)
    leads = get_leads(access_token)
    return JSONResponse(content=leads)

@app.post("/zoho/create_lead")
async def create_user_lead(user_id: str, request: Request):
    lead_data = await request.json()
    refresh_token = get_refresh_token(user_id)
    if not refresh_token:
        raise HTTPException(status_code=400, detail="User not authorized.")
    access_token = get_access_token(refresh_token)
    created = create_lead(access_token, lead_data)
    return JSONResponse(content=created)
