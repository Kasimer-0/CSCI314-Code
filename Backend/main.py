from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Controller import (
    user_admin_controller,
    fundraiser_controller,
    donee_controller,
    platform_manager_controller
)

app = FastAPI(title="CSIT314 Backend - BCE Architecture")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_admin_controller.router)
app.include_router(fundraiser_controller.router)
app.include_router(donee_controller.router)
app.include_router(platform_manager_controller.router)

@app.get("/")
def root():
    return {"message": "BCE Architecture Running Perfectly!"}