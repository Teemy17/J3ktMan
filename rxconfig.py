import reflex as rx
import dotenv
import os

db_url = os.getenv("DATABASE_URL")

assert db_url, "DATABASE_URL not found in .env file"


config = rx.Config(
    app_name="J3ktMan",
    db_url=db_url,
)
