from fastapi import FastAPI
from fast_api.routes import data_routes,langraph_route, download_pdf_route, download_codelab_route

# # Create FastAPI instance
app = FastAPI()

# # Include the routers
app.include_router(data_routes.router, prefix="/data", tags=["Data Operations"])
app.include_router(langraph_routes.router, prefix="/langraph", tags=["LangGraph Operations"])
app.include_router(download_routes.router, prefix="/download", tags=["PDF Download Operations"])
