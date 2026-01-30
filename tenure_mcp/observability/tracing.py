"""OpenTelemetry tracing configuration and utilities."""

import logging
from typing import Optional

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from tenure_mcp.config import settings

logger = logging.getLogger(__name__)

# Global tracer provider
_tracer_provider: Optional[TracerProvider] = None


def initialize_tracing() -> None:
    """Initialize OpenTelemetry tracing with TracerProvider and OTLP exporter.
    
    Configures tracing based on settings:
    - If OTLP endpoint is configured, uses OTLP exporter
    - Otherwise, uses console exporter for development
    - Creates Resource with service name and version
    """
    global _tracer_provider
    
    if not settings.opentelemetry_enabled:
        logger.info("OpenTelemetry tracing is disabled")
        return
    
    if _tracer_provider is not None:
        logger.warning("Tracing already initialized, skipping")
        return
    
    # Create resource with service metadata
    resource = Resource.create(
        {
            "service.name": "tenure-mcp-server",
            "service.version": "0.1.0",
        }
    )
    
    # Create tracer provider
    _tracer_provider = TracerProvider(resource=resource)
    
    # Configure exporter based on settings
    if settings.otlp_endpoint:
        # Use OTLP exporter for production
        # Parse headers if provided as JSON string
        headers = settings.otlp_headers
        if isinstance(headers, str) and headers:
            import json
            try:
                headers = json.loads(headers)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse OTLP_HEADERS as JSON: {headers}")
                headers = {}
        
        otlp_exporter = OTLPSpanExporter(
            endpoint=settings.otlp_endpoint,
            headers=headers if headers else None,
        )
        span_processor = BatchSpanProcessor(otlp_exporter)
        _tracer_provider.add_span_processor(span_processor)
        logger.info(f"Initialized OTLP tracing exporter to {settings.otlp_endpoint}")
    else:
        # Use console exporter for development
        console_exporter = ConsoleSpanExporter()
        span_processor = BatchSpanProcessor(console_exporter)
        _tracer_provider.add_span_processor(span_processor)
        logger.info("Initialized console tracing exporter (development mode)")
    
    # Set as global tracer provider
    trace.set_tracer_provider(_tracer_provider)
    
    logger.info("OpenTelemetry tracing initialized successfully")


def shutdown_tracing() -> None:
    """Shutdown tracing and flush remaining spans."""
    global _tracer_provider
    
    if _tracer_provider is not None:
        _tracer_provider.shutdown()
        _tracer_provider = None
        logger.info("OpenTelemetry tracing shut down")


def get_tracer(name: str) -> trace.Tracer:
    """Get a tracer instance for the given name.
    
    Args:
        name: Tracer name (typically __name__ of the module)
        
    Returns:
        Tracer instance
    """
    return trace.get_tracer(name)
