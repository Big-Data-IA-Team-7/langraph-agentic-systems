# Use a multi-stage build to include Go and Python environments
# Stage 1: Install Go and claat
FROM golang:latest as go-stage

# Set up environment variables for Go
ENV GOPATH=/go
ENV PATH=$GOPATH/bin:/usr/local/go/bin:$PATH

# Create the Go workspace
RUN mkdir -p $GOPATH/{bin,src,pkg}

# Install claat
RUN go install github.com/googlecodelabs/tools/claat@latest

# Stage 2: Main Python Applications
FROM python:3.12.7

# Install dependencies for wkhtmltopdf
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Install Poetry
RUN pip install poetry

# Copy dependencies and install
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Copy application code
COPY ./fast_api /code/fast_api
COPY ./features /code/features
COPY ./navigation /code/navigation
COPY ./streamlit_app.py /code/streamlit_app.py
COPY .env /code/.env

# Copy claat binary from the Go build stage
COPY --from=go-stage /go/bin/claat /usr/local/bin/claat

# Expose necessary ports
EXPOSE 8000 8501

# Start both FastAPI and Streamlit applications along with claat verification
CMD ["/bin/bash", "-c", "uvicorn fast_api.fastapi_setup:app --host 0.0.0.0 --port 8000 --reload & streamlit run streamlit_app.py --server.port 8501"]
