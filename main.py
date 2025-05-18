from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette_context import plugins as context_plugins
from starlette_context.middleware import RawContextMiddleware

from api.v1.routing import RoutingV1
from middlewares import RequestPreProcessor
from middlewares.authentication import AuthenticationContext  # ✅ Ensure correct path

# Global app variable
app = FastAPI()

# Touch Pydantic Encoders (to initialize custom types)
from core import json
json.ENCODERS_BY_TYPE

# 🚨 Order matters: Your custom middlewares should come before context plugins
# 1. Pre-process any incoming request (logging, body parsing, etc.)
app.add_middleware(BaseHTTPMiddleware, dispatch=RequestPreProcessor())

# 2. Starlette Context Middleware with Plugins (includes your JWT decoder)
app.add_middleware(
    RawContextMiddleware,
    plugins=[
        AuthenticationContext(),                # ✅ JWT auth plugin sets context["user"]
        context_plugins.RequestIdPlugin(),      # Optional: Trace ID support
        context_plugins.CorrelationIdPlugin(),  # Optional: Downstream request tracing
    ],
)

# ✅ Versioned route mapping
RoutingV1(app).map_urls()
