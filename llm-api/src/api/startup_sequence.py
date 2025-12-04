from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.helper.loggers import startup_sequence_logger


def startup_sequence():
    startup_sequence_logger.debug("Starting up...")


def shutdown_sequence():
    startup_sequence_logger.debug("Shutting down...")

@asynccontextmanager
async def lifespan(_: FastAPI):
    startup_sequence()
    yield
    shutdown_sequence()