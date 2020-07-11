from fastapi import FastAPI, Header, HTTPException
from typing import List, Optional
from src.handler import handler
import os
import asyncio
import functools

app = FastAPI()


@app.post("/api/update_market_volatility")
async def read_items(x_token: Optional[str] = Header(None)):
    print(x_token)
    if isinstance(x_token, list):
        x_token = x_token[0]
    g_token = os.environ.get("GITHUB_ACCESS_TOKEN")
    if g_token != x_token:
        raise HTTPException(status_code=403, detail="token invalid")
    loop = asyncio.get_event_loop()
    loop.call_soon(functools.partial(handler, x_token))
    return {"status_code": 200, "message": "success: processing request"}
