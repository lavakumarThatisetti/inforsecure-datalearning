from fastapi import FastAPI
import uvicorn
import json
from pydantic import BaseModel
from typing import Dict, Any
import pandas as pd

from api.datalearning import getCustomizedData

app = FastAPI()


#
# class Data(BaseModel):
#     profile: json
#     summary: json
#     transactions: json


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/analyse")
async def root(data: Dict[Any, Any] = None):
    print(str(data['type']).upper())
    return getCustomizedData(data=data)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
