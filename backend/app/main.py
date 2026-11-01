from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router
from .config import allowed_origins, validate_startup_configuration
from .services.auth import initialize_database

app = FastAPI(title="AERM AI API", version="1.0.0")
validate_startup_configuration()
initialize_database()
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
