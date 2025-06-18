from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from zoho_service import (
    generate_auth_url, exchange_code_for_token,
    get_access_token, get_leads, create_lead
)
from storage_service import store_refresh_token, get_refresh_token
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.responses import JSONResponse

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
    try:
        refresh_token = exchange_code_for_token(code)
    except Exception as e:
        return PlainTextResponse(f"Error exchanging code: {e}", status_code=500)

    try:
        store_refresh_token(state, refresh_token)
    except Exception as e:
        return PlainTextResponse(f"Error storing refresh token: {e}", status_code=500)

    html_content = """
    <html>
        <head>
            <title>Authentication Complete</title>
        </head>
        <body>
            <h3>✅ Authentication successful!</h3>
            <p>You may now return to the app.</p>
            <p><strong>You can close this tab.</strong></p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content) 
@app.get("/zoho/auth-status")
def check_auth_status(user_id: str):
    
    refresh_token = get_refresh_token(user_id)
    if refresh_token:
        return {"auth_done": True}
    return {"auth_done": False}
@app.get("/zoho/get_leads")
def get_user_leads(user_id: str):
    refresh_token = get_refresh_token(user_id)
    if not refresh_token:
        raise HTTPException(status_code=400, detail="User not authorized.")
    access_token = get_access_token(refresh_token)
    leads = get_leads(access_token)
    return JSONResponse(content=leads)
@app.delete("/zoho/delete_token")
def delete_token(user_id: str):
    try:
        delete_refresh_token(user_id)
        return JSONResponse(content={"status": f"Refresh token for user {user_id} deleted."}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting token: {e}")

@app.post("/zoho/create_lead")
async def create_user_lead(user_id: str, request: Request):
    lead_data = await request.json()
    refresh_token = get_refresh_token(user_id)
    if not refresh_token:
        raise HTTPException(status_code=400, detail="User not authorized.")
    access_token = get_access_token(refresh_token)
    created = create_lead(access_token, lead_data)
    return JSONResponse(content=created)
