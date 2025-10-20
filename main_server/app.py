# main_server/app.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
import httpx

app = FastAPI(title="Main Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ENTITY_SERVER = "http://127.0.0.1:5001"
STATUS_SERVICE = "http://127.0.0.1:5002"

VALID_SERVICES = {
    "entity": ENTITY_SERVER,
    "status": STATUS_SERVICE
}

@app.api_route("/{service}/{path:path}", methods=["GET","POST","PUT","DELETE"])
async def gateway(service: str, path: str, request: Request):
    target_base = VALID_SERVICES.get(service)
    if not target_base:
        return JSONResponse({"error": "Unknown service"}, status_code=400)
    target = f"{target_base}/{path}"

    body = await request.body()
    headers = dict(request.headers)

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.request(request.method, target, headers=headers, content=body)
    except httpx.RequestError as e:
        return JSONResponse({"error": f"Service unreachable: {str(e)}"}, status_code=503)

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=dict(resp.headers),
        media_type=resp.headers.get("content-type")
    )
