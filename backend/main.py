import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

import database
from routers import users, tasks


app = FastAPI(title="Personal Task Manager API")


database.init_db()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time

    print(
        f"{request.method} {request.url.path} "
        f"Status: {response.status_code} "
        f"Time: {process_time:.4f}s"
    )

    return response


app.include_router(users.router)
app.include_router(tasks.router)


@app.get("/")
def home():
    return {"message": "Personal Task Manager API Running"}