from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import init_db
from app.routers import cart, chat, products, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="ShopFast API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(cart.router)
app.include_router(users.router)
app.include_router(chat.router)


@app.get("/", tags=["health"])
def root():
    return {"message": "Welcome to the ecommerce Fast API"}


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
