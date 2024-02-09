from fastapi import FastAPI

from core import RetrievalPipeline

app = FastAPI()

@app.get("/moments/{prompt}")
async def retrive_moments(prompt):
    rp = RetrievalPipeline()
    return rp.retrive(str(prompt))

@app.get("/hi")
async def get_hi():
    return "hi"