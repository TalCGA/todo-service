from fastapi import FastAPI


app = FastAPI(title="ToDo Service")

@app.get("/")
def root():
    return {"message": "backend check"}
