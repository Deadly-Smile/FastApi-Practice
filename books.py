from fastapi import FastAPI

app = FastAPI()

@app.get('/')
async def get_fast_api():
    return {"message": "Hello World"}

