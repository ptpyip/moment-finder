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

@app.get("/moment/test")
async def test_db():
    rp = RetrievalPipeline()
    return rp.db.test_connection()

# if __name__ == "__main":
#     app.l