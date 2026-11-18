from fastapi import FastAPI

app = FastAPI(title="Job Market Radar API")


@app.get("/health")
def health_check():
    return {"status": "ok"}
