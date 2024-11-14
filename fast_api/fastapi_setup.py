from fastapi import FastAPI
from fast_api.routes import data_routes

# # Create FastAPI instance
app = FastAPI()

# # Include the routers
app.include_router(data_routes.router, prefix="/data", tags=["Data Operations"])