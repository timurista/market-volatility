from fastapi import FastAPI, Header, HTTPException
from typing import List, Optional
from src.handler import handler
from src.etrade import handler as etrade_handler
from src.alpaca import handler as alpaca_handler
from pydantic import BaseModel

import os
import asyncio
import functools

app = FastAPI()


@app.post("/api/update_market_volatility")
async def read_items(x_token: Optional[str] = Header(None)):
    if isinstance(x_token, list):
        x_token = x_token[0]
    g_token = os.environ.get("GITHUB_ACCESS_TOKEN")
    if g_token != x_token:
        raise HTTPException(status_code=403, detail="token invalid")
    loop = asyncio.get_event_loop()
    loop.call_soon(functools.partial(handler, x_token))
    return {"status_code": 200, "message": "success: processing request"}

class Item(BaseModel):
    name: str
    order: str
    contracts: float
    pos_size: float
    ticker: str
    api_key: str

@app.post("/api/execute_alpaca_trade")
async def read_items(item: Item):
    access_key = os.environ.get("SECRET_ETRADE_TOKEN")
    print(item)
    if item.api_key != access_key:
        raise HTTPException(status_code=403, detail="token invalid")
    balance = alpaca_handler(item)
    return {"status_code": 200, "message": balance}


@app.post("/api/execute_etrade")
async def read_items(item):
    print(item)
    access_key = os.environ.get("SECRET_ETRADE_TOKEN")
    if item['api_key'] != access_key:
        raise HTTPException(status_code=403, detail="token invalid")
    # loop = asyncio.get_event_loop()
    balance = etrade_handler(item)
    # loop.call_soon(functools.partial(handler))
    return {"status_code": 200, "message": balance}
