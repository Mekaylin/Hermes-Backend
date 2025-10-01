from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import health, market, predict, recommendations, news, agent
from db import init_db

app = FastAPI(title="Hermes Trading Companion")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.on_event("startup")
async def startup_event():
    # Initialize DB (creates tables if missing)
    init_db()


# Include routers
app.include_router(health.router, prefix="")
app.include_router(market.router, prefix="/market")
app.include_router(predict.router, prefix="/predict")
app.include_router(recommendations.router, prefix="/recommendations")
app.include_router(news.router, prefix="/news")
app.include_router(agent.router, prefix="/api")
