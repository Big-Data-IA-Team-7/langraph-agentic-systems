from fastapi import FastAPI
from fast_api.routes import data_routes,langraph_route, download_pdf_route, download_codelab_route

# # Create FastAPI instance
app = FastAPI()

# # Include the routers
app.include_router(data_routes.router, prefix="/data", tags=["Data Operations"])
app.include_router(langraph_route.router, prefix="/langraph", tags=["LangGraph Operations"])
app.include_router(download_pdf_route.router, prefix="/pdf", tags=["PDF Download Operations"])
app.include_router(download_codelab_route.router, prefix="/index", tags=["CodeLab Download Operations"])
