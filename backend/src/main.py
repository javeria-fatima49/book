import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from redis.asyncio import Redis
from src.core.config import REDIS_URL
from src.api import rag, translate

# Configure basic logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    if REDIS_URL:
        redis = Redis.from_url(REDIS_URL, encoding="utf8", decode_responses=True)
        await FastAPILimiter.init(redis)
        logger.info("FastAPI Limiter initialized.")
    else:
        logger.warning("REDIS_URL is not set. FastAPI Limiter will not be initialized.")


@app.on_event("shutdown")
async def shutdown():
    await FastAPILimiter.shutdown()
    logger.info("FastAPI Limiter shutdown.")


app.include_router(rag.router, prefix="/api/v1/rag")
app.include_router(translate.router, prefix="/api/v1")


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTPException: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )


@app.get("/")
def read_root():
    return {"Hello": "World"}
