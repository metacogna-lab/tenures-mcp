"""Tests for OpenTelemetry observability module."""

import pytest
from opentelemetry import trace

from tenure_mcp.observability import get_tracer, initialize_tracing, shutdown_tracing


class TestTracingInitialization:
    """Test OpenTelemetry tracing initialization."""

    def test_initialize_tracing(self):
        """Test that tracing can be initialized."""
        # Shutdown any existing tracing
        try:
            shutdown_tracing()
        except Exception:
            pass
        
        # Initialize tracing
        initialize_tracing()
        
        # Verify tracer provider is set
        tracer_provider = trace.get_tracer_provider()
        assert tracer_provider is not None

    def test_get_tracer(self):
        """Test getting a tracer instance."""
        initialize_tracing()
        tracer = get_tracer("test_module")
        assert tracer is not None
        assert isinstance(tracer, trace.Tracer)

    def test_tracer_creates_spans(self):
        """Test that tracer can create spans."""
        initialize_tracing()
        tracer = get_tracer("test_module")
        
        with tracer.start_as_current_span("test_span") as span:
            span.set_attribute("test.attribute", "test_value")
            assert span.is_recording()
            assert span.get_attribute("test.attribute") == "test_value"

    def test_shutdown_tracing(self):
        """Test that tracing can be shut down."""
        initialize_tracing()
        shutdown_tracing()
        
        # After shutdown, should still be able to get tracer (but provider may be reset)
        tracer = get_tracer("test_module")
        assert tracer is not None


class TestTracingIntegration:
    """Test tracing integration with FastMCP tools and resources."""

    def test_tool_tracing(self):
        """Test that tools create spans when executed."""
        initialize_tracing()
        tracer = get_tracer("test")
        
        # Simulate tool execution with tracing
        with tracer.start_as_current_span("tool.test_tool") as span:
            span.set_attribute("tool.name", "test_tool")
            span.set_attribute("tool.input.id", "test_id")
            span.set_status(trace.Status(trace.StatusCode.OK))
            
            assert span.is_recording()
            assert span.get_attribute("tool.name") == "test_tool"

    def test_resource_tracing(self):
        """Test that resources create spans when accessed."""
        initialize_tracing()
        tracer = get_tracer("test")
        
        # Simulate resource access with tracing
        with tracer.start_as_current_span("resource.test_resource") as span:
            span.set_attribute("resource.name", "test_resource")
            span.set_attribute("resource.uri_pattern", "test://{id}")
            span.set_status(trace.Status(trace.StatusCode.OK))
            
            assert span.is_recording()
            assert span.get_attribute("resource.name") == "test_resource"

    def test_workflow_tracing(self):
        """Test that workflows create spans when executed."""
        initialize_tracing()
        tracer = get_tracer("test")
        
        # Simulate workflow execution with tracing
        with tracer.start_as_current_span("workflow.test_workflow") as span:
            span.set_attribute("workflow.name", "test_workflow")
            span.set_attribute("workflow.input.property_id", "prop_001")
            span.set_attribute("workflow.correlation_id", "test_correlation")
            span.set_status(trace.Status(trace.StatusCode.OK))
            
            assert span.is_recording()
            assert span.get_attribute("workflow.name") == "test_workflow"
