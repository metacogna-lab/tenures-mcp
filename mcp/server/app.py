"""FastAPI application factory."""

import json
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from mcp.config import settings
from mcp.policy import get_policy_gateway
from mcp.resources import get_resource_registry, register_resource
from mcp.resources.implementations import (
    get_ledger_summary_resource,
    get_property_details_resource,
    get_property_documents_resource,
    get_property_feedback_resource,
)
from mcp.schemas.base import (
    ErrorResponse,
    RequestContext,
    ToolExecutionRequest,
    ToolExecutionResponse,
)
from mcp.server.middleware import (
    authentication_middleware,
    observability_middleware,
    request_id_middleware,
)
from mcp.storage import get_db
from mcp.tools import get_tool_registry, register_tool
from mcp.tools.implementations import (
    analyze_open_home_feedback,
    calculate_breach_status,
    extract_expiry_date,
    generate_vendor_report,
    ocr_document,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager for startup/shutdown."""
    # Startup: Register tools and resources
    registry = get_tool_registry()

    # Register tools
    register_tool("analyze_open_home_feedback", analyze_open_home_feedback)
    register_tool("calculate_breach_status", calculate_breach_status)
    register_tool("ocr_document", ocr_document)
    register_tool("extract_expiry_date", extract_expiry_date)
    register_tool("generate_vendor_report", generate_vendor_report)

    # Register Tier C (mutation/high-risk) tools
    from mcp.tools.implementations import prepare_breach_notice

    register_tool("prepare_breach_notice", prepare_breach_notice)

    # Register mutation tools (Tier C)
    from mcp.tools.mutation_tools import prepare_breach_notice

    register_tool("prepare_breach_notice", prepare_breach_notice)

    # Register resources
    resource_registry = get_resource_registry()
    register_resource(
        "vault://properties/{id}/details",
        lambda property_id, context: get_property_details_resource(property_id, context),
    )
    register_resource(
        "vault://properties/{id}/feedback",
        lambda property_id, context: get_property_feedback_resource(property_id, context),
    )
    register_resource(
        "ailo://ledgers/{tenancy_id}/summary",
        lambda tenancy_id, context: get_ledger_summary_resource(tenancy_id, context),
    )
    register_resource(
        "vault://properties/{id}/documents",
        lambda property_id, context: get_property_documents_resource(property_id, context),
    )

    # Register Tier A agents
    from mcp.agents.tier_a_agents import register_tier_a_agents

    register_tier_a_agents()

    # Register Tier B agents
    from mcp.agents.tier_b_agents import register_tier_b_agents

    register_tier_b_agents()

    # Register Tier C agents
    from mcp.agents.tier_c_agents import register_tier_c_agents

    register_tier_c_agents()

    # Register mutation tools
    from mcp.tools.mutation_tools import prepare_breach_notice

    register_tool("prepare_breach_notice", prepare_breach_notice)

    # Register Tier C agents
    from mcp.agents.tier_c_agents import register_tier_c_agents

    register_tier_c_agents()

    # Register Tier C agents
    from mcp.agents.tier_c_agents import register_tier_c_agents

    register_tier_c_agents()

    # Register workflows
    from mcp.langgraphs import register_workflow
    from mcp.langgraphs.executor import get_workflow_executor

    executor = get_workflow_executor()
    register_workflow("weekly_vendor_report", executor.execute_weekly_vendor_report)
    register_workflow("arrears_detection", executor.execute_arrears_detection)
    register_workflow("compliance_audit", executor.execute_compliance_audit)

    yield

    # Shutdown: cleanup if needed
    pass


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Tenure MCP Server",
        description="MCP Server for Tenure RE Tech - Ray White real estate agentic workflows",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Add middleware (order matters)
    app.middleware("http")(request_id_middleware)
    app.middleware("http")(authentication_middleware)
    if settings.opentelemetry_enabled:
        app.middleware("http")(observability_middleware)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, restrict to specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check
    @app.get("/healthz")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "version": "0.1.0"}

    # Version endpoint
    @app.get("/version")
    async def get_version():
        """Get API version."""
        return {
            "version": "0.1.0",
            "api_version": settings.mcp_api_version,
        }

    # Metrics endpoint (stub for Prometheus)
    @app.get("/metrics")
    async def get_metrics():
        """Prometheus-compatible metrics endpoint."""
        # In production, would export actual metrics
        return "# Metrics endpoint\n# Prometheus metrics would be exported here\n"

    # Tool execution endpoint
    @app.post(f"/{settings.mcp_api_version}/tools/{{tool_name}}")
    async def execute_tool(
        tool_name: str,
        request: ToolExecutionRequest,
        hitl_token: str | None = Header(None, alias="X-HITL-Token"),
    ):
        """Execute a tool."""
        import time

        start_time = time.time()
        correlation_id = request.correlation_id
        context = request.context

        # Validate request context
        policy_gateway = get_policy_gateway()
        context_valid, context_error = policy_gateway.check_request_context(context)
        if not context_valid:
            policy_gateway.log_policy_decision(
                correlation_id, context, tool_name, False, context_error
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=context_error,
            )

        # Check RBAC policy
        allowed, policy_error = policy_gateway.check_rbac(context, tool_name, hitl_token)
        if not allowed:
            policy_gateway.log_policy_decision(
                correlation_id, context, tool_name, False, policy_error
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=policy_error or "Access denied",
            )

        policy_gateway.log_policy_decision(correlation_id, context, tool_name, True)

        # Get tool from registry
        tool_func = get_tool_registry().get(tool_name)
        if not tool_func:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tool '{tool_name}' not found",
            )

            # Execute tool
        try:
            # Parse input based on tool name (in production, would use schema registry)
            from mcp.schemas.tools import (
                AnalyzeFeedbackInput,
                CalculateBreachInput,
                ExtractExpiryInput,
                GenerateVendorReportInput,
                OCRDocumentInput,
                PrepareBreachNoticeInput,
            )

            input_schema_map = {
                "analyze_open_home_feedback": AnalyzeFeedbackInput,
                "calculate_breach_status": CalculateBreachInput,
                "ocr_document": OCRDocumentInput,
                "extract_expiry_date": ExtractExpiryInput,
                "generate_vendor_report": GenerateVendorReportInput,
                "prepare_breach_notice": None,  # Custom input class
            }

            schema_class = input_schema_map.get(tool_name)
            if schema_class is None and tool_name != "prepare_breach_notice":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unknown tool schema for '{tool_name}'",
                )

            # Handle mutation tools with custom input classes
            if tool_name == "prepare_breach_notice":
                from mcp.tools.mutation_tools import PrepareBreachNoticeInput

                tool_input = PrepareBreachNoticeInput(
                    tenancy_id=request.input_data["tenancy_id"],
                    breach_reason=request.input_data["breach_reason"],
                )
            else:
                # Special handling for prepare_breach_notice (takes dict input)
            if tool_name == "prepare_breach_notice":
                # For mutation tools, we pass the raw input dict
                output = await tool_func(request.input_data, context)
            else:
                tool_input = schema_class(**request.input_data)
                output = await tool_func(tool_input, context)

            # Redact output if needed
            if hasattr(output, "model_dump"):
                output_dict = output.model_dump()
            elif isinstance(output, dict):
                output_dict = output
            else:
                output_dict = {"data": str(output)}

            # For mutation tools, log pre/post state
            if tool_name in policy_gateway.MUTATION_TOOLS:
                # Log pre-state (input)
                db.log_audit_event(
                    correlation_id=correlation_id,
                    event_type="mutation_pre_state",
                    user_id=context.user_id,
                    tenant_id=context.tenant_id,
                    tool_name=tool_name,
                    action="pre_execution",
                    details={"input_state": request.input_data},
                )

            redacted_output = policy_gateway.redact_output(output_dict, context, tool_name)

            # For mutation tools, log post-state
            if tool_name in policy_gateway.MUTATION_TOOLS:
                db.log_audit_event(
                    correlation_id=correlation_id,
                    event_type="mutation_post_state",
                    user_id=context.user_id,
                    tenant_id=context.tenant_id,
                    tool_name=tool_name,
                    action="post_execution",
                    details={"output_state": redacted_output},
                )

            execution_time_ms = (time.time() - start_time) * 1000

            # Log execution (with full state for mutation tools)
            db = get_db()

            # For mutation tools, log pre/post state
            if tool_name in ["prepare_breach_notice"]:
                # Log pre-state
                db.log_audit_event(
                    correlation_id=correlation_id,
                    event_type="mutation_pre_state",
                    user_id=context.user_id,
                    tenant_id=context.tenant_id,
                    tool_name=tool_name,
                    action="pre_execution",
                    details={"input": request.input_data},
                )

            db.log_tool_execution(
                correlation_id=correlation_id,
                tool_name=tool_name,
                user_id=context.user_id,
                tenant_id=context.tenant_id,
                input_data=request.input_data,
                output_data=redacted_output,
                execution_time_ms=execution_time_ms,
                trace_id=getattr(request.state, "trace_id", None),
                success=True,
            )

            # Log post-state for mutation tools
            if tool_name in ["prepare_breach_notice"]:
                db.log_audit_event(
                    correlation_id=correlation_id,
                    event_type="mutation_post_state",
                    user_id=context.user_id,
                    tenant_id=context.tenant_id,
                    tool_name=tool_name,
                    action="post_execution",
                    details={"output": redacted_output},
                )

            return ToolExecutionResponse(
                success=True,
                correlation_id=correlation_id,
                tool_name=tool_name,
                output_data=redacted_output,
                execution_time_ms=execution_time_ms,
                trace_id=getattr(request.state, "trace_id", None),
            )

        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            error_message = str(e)

            # Log error
            db = get_db()
            db.log_tool_execution(
                correlation_id=correlation_id,
                tool_name=tool_name,
                user_id=context.user_id,
                tenant_id=context.tenant_id,
                input_data=request.input_data,
                output_data=None,
                execution_time_ms=execution_time_ms,
                trace_id=getattr(request.state, "trace_id", None),
                success=False,
                error_message=error_message,
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Tool execution failed: {error_message}",
            )

    # Workflow execution endpoint
    @app.post(f"/{settings.mcp_api_version}/workflows/{{workflow_name}}")
    async def execute_workflow(
        workflow_name: str,
        request: Request,
        user_id: str = Header(..., alias="X-User-ID"),
        tenant_id: str = Header(..., alias="X-Tenant-ID"),
        auth_context: str = Header(..., alias="X-Auth-Context"),
        role: str = Header(default="agent", alias="X-Role"),
    ):
        """Execute a LangGraph workflow."""
        import json

        correlation_id = request.state.correlation_id
        body = await request.json()

        # Build request context
        context = RequestContext(
            user_id=user_id,
            tenant_id=tenant_id,
            auth_context=auth_context,
            role=role,
        )

        # Validate context
        policy_gateway = get_policy_gateway()
        context_valid, context_error = policy_gateway.check_request_context(context)
        if not context_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=context_error,
            )

        # Get workflow executor
        from mcp.langgraphs.executor import get_workflow_executor

        executor = get_workflow_executor()

        try:
            if workflow_name == "weekly_vendor_report":
                property_id = body.get("property_id")
                if not property_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Missing property_id",
                    )
                result = await executor.execute_weekly_vendor_report(property_id, context)

            elif workflow_name == "arrears_detection":
                tenancy_id = body.get("tenancy_id")
                if not tenancy_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Missing tenancy_id",
                    )
                result = await executor.execute_arrears_detection(tenancy_id, context)

            elif workflow_name == "compliance_audit":
                property_id = body.get("property_id")
                if not property_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Missing property_id",
                    )
                result = await executor.execute_compliance_audit(property_id, context)

            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Workflow '{workflow_name}' not found",
                )

            return result

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Workflow execution failed: {str(e)}",
            )

    # Resource retrieval endpoint
    @app.get(f"/{settings.mcp_api_version}/resources/{{resource_path:path}}")
    async def get_resource(
        resource_path: str,
        user_id: str = Header(..., alias="X-User-ID"),
        tenant_id: str = Header(..., alias="X-Tenant-ID"),
        auth_context: str = Header(..., alias="X-Auth-Context"),
        role: str = Header(default="agent", alias="X-Role"),
    ):
        """Get a resource."""
        correlation_id = str(uuid.uuid4())

        # Build request context
        context = RequestContext(
            user_id=user_id,
            tenant_id=tenant_id,
            auth_context=auth_context,
            role=role,
        )

        # Validate context
        policy_gateway = get_policy_gateway()
        context_valid, context_error = policy_gateway.check_request_context(context)
        if not context_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=context_error,
            )

        # Get resource handler
        resource_registry = get_resource_registry()
        handler_result = resource_registry.get(resource_path)
        if not handler_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resource '{resource_path}' not found",
            )

        handler_func, metadata = handler_result

        # Extract ID from URI (simple parsing)
        # In production, would use proper URI routing
        parts = resource_path.split("/")
        resource_id = parts[-1] if parts else None

        try:
            # Call resource handler
            result = await handler_func(resource_id, context)

            # Redact if needed
            redacted_result = policy_gateway.redact_output(
                result if isinstance(result, dict) else {"data": result},
                context,
                resource_path,
            )

            return {
                "success": True,
                "correlation_id": correlation_id,
                "resource_path": resource_path,
                "data": redacted_result,
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Resource retrieval failed: {str(e)}",
            )

    return app
