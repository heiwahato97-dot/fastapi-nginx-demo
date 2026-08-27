from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {
        "message": "Hello through Nginx"
    }


@app.get("/api/status")
def status():
    return {
        "status": "ok",
        "server": "FastAPI"
    }