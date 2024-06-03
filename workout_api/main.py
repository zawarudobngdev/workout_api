from fastapi import FastAPI
from fastapi_pagination import add_pagination
from fastapi_pagination.utils import disable_installed_extensions_check

from workout_api.routers import api_router

app = FastAPI(title="Workout API")
app.include_router(api_router)

add_pagination(app)
disable_installed_extensions_check()
