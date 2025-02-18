import uvicorn
import redis

from redis_lru import RedisLRU
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse

from src.conf import messages

from src.api import utils, contacts, users, auth

app = FastAPI()
app.include_router(utils.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")

client = redis.StrictRedis(host="localhost", port=6379, password=None)
cache = RedisLRU(client)

origins = ["<http://localhost:8000>"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "error": f"Перевищено ліміт запитів ({exc.detail}). Спробуйте пізніше."
        },
    )

@app.get("/")
async def root():
    return {"message": messages.WELCOME_MESSAGE}

if __name__ == "__main__":

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, workers=1)