# main.py
import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from course_recommender.api.courses import router as courses_router
from course_recommender.api.recommendations import router as recs_router
from course_recommender.services import RecommenderService
from course_recommender.settings import settings


def create_app() -> FastAPI:
    # Configure logging once
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )
    logger = logging.getLogger("course_recommender_api")
    logger.info("Starting Course Recommendation API")

    app = FastAPI(title="Course Recommendation API")

    # -----------------------------------------------------
    # CORS MIDDLEWARE  (needed for React frontend)
    # -----------------------------------------------------
    origins = [
        "http://localhost:5173",   # React default for CRA
        "https://course-recommender-frontend.vercel.app",   # Vite default
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -----------------------------------------------------
    # INITIALIZE RECOMMENDER ON STARTUP
    # -----------------------------------------------------
    @app.on_event("startup")
    def startup_event() -> None:
        app.state.recommender = RecommenderService()

    # -----------------------------------------------------
    # EXCEPTION HANDLERS
    # -----------------------------------------------------
    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        logger.warning("Request validation error on %s: %s", request.url, exc.errors())
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Invalid request payload",
                "errors": exc.errors(),
            },
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_handler(
        request: Request,
        exc: ValidationError,
    ) -> JSONResponse:
        logger.warning("Pydantic validation error on %s: %s", request.url, exc.errors())
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Invalid data",
                "errors": exc.errors(),
            },
        )

    # -----------------------------------------------------
    # ROUTERS
    # -----------------------------------------------------
    app.include_router(courses_router)
    app.include_router(recs_router)

    return app


app = create_app()
