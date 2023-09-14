import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def create_app(**kwargs):
    app = FastAPI()
    add_cors(app)
    mount_routes(app)
    return app


def mount_routes(app):
    from .user_api import user_app
    from .auth_api import auth_app

    app.mount("/library/auth", auth_app)
    app.mount("/library", user_app)


def add_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=os.getenv("CORS_DOMAINS", "*").split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
