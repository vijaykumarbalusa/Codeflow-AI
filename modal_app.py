"""
Modal deployment for CodeFlow AI
Uses proper file mounting
"""

import modal

app = modal.App("codeflow-ai")

# Build image with dependencies
image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install(
        "fastapi==0.109.0",
        "uvicorn[standard]==0.27.0",
        "pydantic==2.5.0",
        "pydantic-settings==2.1.0",
        "python-dotenv==1.0.0",
        "httpx==0.26.0",
        "PyGithub==2.1.1",
        "groq==0.4.1",
        "qdrant-client==1.7.0",
        "sentence-transformers==2.3.0",
        "PyJWT==2.8.0",
        "cryptography==41.0.7",
    )
)


@app.function(
    image=image,
    secrets=[modal.Secret.from_name("codeflow-secrets")],
    mounts=[
        modal.Mount.from_local_dir("src", remote_path="/root/src"),
        modal.Mount.from_local_file("config/private-key.pem", remote_path="/root/config/private-key.pem"),
    ],
    min_containers=1,
    timeout=300,
)
@modal.asgi_app()
def fastapi_app():
    """FastAPI application"""
    import sys
    sys.path.insert(0, "/root")
    
    from src.codeflow.main import app
    return app