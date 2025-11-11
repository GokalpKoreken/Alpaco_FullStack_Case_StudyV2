from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routers import admin, auth, drops


def create_application() -> FastAPI:
    app = FastAPI(title="DropSpot API", version="0.1.0")

    app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:3000",
                "http://127.0.0.1:3000",
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
    )

    app.include_router(auth.router)
    app.include_router(drops.router)
    app.include_router(admin.router)

    @app.get("/health", tags=["system"])
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_application()


@app.on_event("startup")
def on_startup() -> None:
    init_db()
