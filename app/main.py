from fastapi import FastAPI, HTTPException
import random
import time

app = FastAPI()

@app.get("/ping")
def ping():
    return {"status": "ok"}

@app.post("/login")
def login(username: str, password: str):
    if username == "admin" and password == "password":
        return {"message": "Login successful"}
    raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/data")
def get_data():

    time.sleep(random.uniform(0.1, 0.5))
    return {"data": random.randint(1, 100)}

@app.get("/unstable")
def unstable():

    if random.random() < 0.2:
        raise HTTPException(status_code=500, detail="Random failure")
    return {"status": "stable"}
