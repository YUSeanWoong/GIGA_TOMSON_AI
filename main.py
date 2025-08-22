from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "시발 세상아!!!!!!!!!!!"}