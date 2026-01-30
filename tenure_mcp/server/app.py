"""FastAPI application factory."""

import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware

from tenure_mcp.config import settings
from tenure_mcp.policy import get_policy_gateway
from tenure_mcp.resources import get_resource_registry, register_resource
from tenure_mcp.resources.implementations import (
    get_ledger_summary_resource,
    get_property_details_resource,
    get_property_documents_resource,
    get_property_feedback_resource,
)
from tenure_mcp.schemas.agent import AgentQueryInput
from tenure_mcp.schemas.base import (
    RequestContext,
    ToolExecutionRequest,
    ToolExecutionResponse,
)
from tenure_mcp.server.middleware import (
    authentication_middleware,
    observability_middleware,
    request_id_middleware,
)
from tenure_mcp.server.sse import sse_app
from tenure_mcp.langgraphs.agent import execute_query_agent
from tenure_mcp.storage import get_db
from tenure_mcp.tools import get_tool_registry, register_tool
from tenure_mcp.tools.implementations import (
    analyze_open_home_feedback,
    calculate_breach_status,
    extract_expiry_date,
    generate_vendor_report,
    ocr_document,
    prepare_breach_notice,
    web_search,
)
from tenure_mcp.tools.integration_tools import (
    fetch_property_emails,
    search_communication_threads,
    list_property_documents,
    get_document_content,
    check_document_expiry,
    list_active_properties,
    get_property_contacts,
    get_upcoming_open_homes,
    list_arrears_tenancies,
    get_tenant_communication_history,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager for startup/shutdown."""
    # Startup: Register tools and resources
    # Register existing tools
    register_tool("analyze_open_home_feedback", analyze_open_home_feedback)
    register_tool("calculate_breach_status", calculate_breach_status)
    register_tool("ocr_document", ocr_document)
    register_tool("extract_expiry_date", extract_expiry_date)
    register_tool("generate_vendor_report", generate_vendor_report)
    register_tool("prepare_breach_notice", prepare_breach_notice)  # Tier C - HITL required
    register_tool("web_search", web_search)  # Read-only; use when query needs current/external info

    # Register Gmail integration tools
    register_tool("fetch_property_emails", fetch_property_emails)
    register_tool("search_communication_threads", search_communication_threads)

    # Register Google Drive integration tools
    register_tool("list_property_documents", list_property_documents)
    register_tool("get_document_content", get_document_content)
    register_tool("check_document_expiry", check_document_expiry)

    # Register VaultRE integration tools
    register_tool("list_active_properties", list_active_properties)
    register_tool("get_property_contacts", get_property_contacts)
    register_tool("get_upcoming_open_homes", get_upcoming_open_homes)

    # Register Ailo integration tools
    register_tool("list_arrears_tenancies", list_arrears_tenancies)
    register_tool("get_tenant_communication_history", get_tenant_communication_history)

    # Register resources
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
    from tenure_mcp.agents.tier_a_agents import register_tier_a_agents

    register_tier_a_agents()

    # Register Tier B agents
    from tenure_mcp.agents.tier_b_agents import register_tier_b_agents

    register_tier_b_agents()

    # Register Tier C agents
    from tenure_mcp.agents.tier_c_agents import register_tier_c_agents

    register_tier_c_agents()

    # Register workflows
    from tenure_mcp.langgraphs import register_workflow
    from tenure_mcp.langgraphs.executor import get_workflow_executor

    executor = get_workflow_executor()
    register_workflow("weekly_vendor_report", executor.execute_weekly_vendor_report)
    register_workflow("arrears_detection", executor.execute_arrears_detection)
    register_workflow("compliance_audit", executor.execute_compliance_audit)
    register_workflow("unified_collection", executor.execute_unified_collection)

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

    # Add middleware (order matters - runs in REVERSE order of registration)
    # So we want: request_id -> auth -> observability (for actual request flow)
    # Register observability first, then auth, then request_id
    if settings.opentelemetry_enabled:
        app.middleware("http")(observability_middleware)
    app.middleware("http")(authentication_middleware)
    app.middleware("http")(request_id_middleware)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, restrict to specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount MCP SSE transport at /sse for LLM agent integration
    app.mount("/sse", sse_app)

    # Health check (liveness probe)
    @app.get("/healthz")
    async def health_check():
        """Liveness health check endpoint."""
        return {"status": "healthy", "version": "0.1.0"}

    # Readiness check (readiness probe)
    @app.get("/ready")
    async def readiness_check():
        """Readiness check - verifies all dependencies are available."""
        checks = {
            "database": False,
            "tools_registered": False,
            "resources_registered": False,
        }

        # Check database connectivity
        try:
            db = get_db()
            with db.get_connection() as conn:
                conn.execute("SELECT 1")
            checks["database"] = True
        except Exception:
            pass

        # Check tools are registered
        tool_registry = get_tool_registry()
        checks["tools_registered"] = len(tool_registry._tools) > 0

        # Check resources are registered
        resource_registry = get_resource_registry()
        checks["resources_registered"] = len(resource_registry.list_resources()) > 0

        all_ready = all(checks.values())
        return {
            "status": "ready" if all_ready else "not_ready",
            "checks": checks,
            "version": "0.1.0",
        }

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
        tool_request: ToolExecutionRequest,
        http_request: Request,
        hitl_token: str | None = Header(None, alias="X-HITL-Token"),
    ):
        """Execute a tool."""
        import time

        start_time = time.time()
        correlation_id = tool_request.correlation_id
        context = tool_request.context

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
            from tenure_mcp.schemas.tools import (
                AnalyzeFeedbackInput,
                CalculateBreachInput,
                ExtractExpiryInput,
                GenerateVendorReportInput,
                OCRDocumentInput,
                PrepareBreachNoticeInput,
                WebSearchInput,
            )
            from tenure_mcp.schemas.integrations import (
                FetchPropertyEmailsInput,
                SearchCommunicationThreadsInput,
                ListPropertyDocumentsInput,
                GetDocumentContentInput,
                CheckDocumentExpiryInput,
                ListActivePropertiesInput,
                GetPropertyContactsInput,
                GetUpcomingOpenHomesInput,
                ListArrearsTenanciesInput,
                GetTenantCommunicationHistoryInput,
            )

            input_schema_map = {
                # Existing tools
                "analyze_open_home_feedback": AnalyzeFeedbackInput,
                "calculate_breach_status": CalculateBreachInput,
                "ocr_document": OCRDocumentInput,
                "extract_expiry_date": ExtractExpiryInput,
                "generate_vendor_report": GenerateVendorReportInput,
                "prepare_breach_notice": PrepareBreachNoticeInput,
                "web_search": WebSearchInput,
                # Gmail integration tools
                "fetch_property_emails": FetchPropertyEmailsInput,
                "search_communication_threads": SearchCommunicationThreadsInput,
                # Google Drive integration tools
                "list_property_documents": ListPropertyDocumentsInput,
                "get_document_content": GetDocumentContentInput,
                "check_document_expiry": CheckDocumentExpiryInput,
                # VaultRE integration tools
                "list_active_properties": ListActivePropertiesInput,
                "get_property_contacts": GetPropertyContactsInput,
                "get_upcoming_open_homes": GetUpcomingOpenHomesInput,
                # Ailo integration tools
                "list_arrears_tenancies": ListArrearsTenanciesInput,
                "get_tenant_communication_history": GetTenantCommunicationHistoryInput,
            }

            schema_class = input_schema_map.get(tool_name)
            if not schema_class:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unknown tool schema for '{tool_name}'",
                )

            tool_input = schema_class(**tool_request.input_data)
            output = await tool_func(tool_input, context)

            # Redact output if needed
            if hasattr(output, "model_dump"):
                output_dict = output.model_dump()
            elif isinstance(output, dict):
                output_dict = output
            else:
                output_dict = {"data": str(output)}

            redacted_output = policy_gateway.redact_output(output_dict, context, tool_name)
            execution_time_ms = (time.time() - start_time) * 1000

            # Log execution
            db = get_db()

            # For mutation tools, log pre/post state
            if tool_name in policy_gateway.MUTATION_TOOLS:
                db.log_audit_event(
                    correlation_id=correlation_id,
                    event_type="mutation_pre_state",
                    user_id=context.user_id,
                    tenant_id=context.tenant_id,
                    tool_name=tool_name,
                    action="pre_execution",
                    details={"input": tool_request.input_data},
                )

            db.log_tool_execution(
                correlation_id=correlation_id,
                tool_name=tool_name,
                user_id=context.user_id,
                tenant_id=context.tenant_id,
                input_data=tool_request.input_data,
                output_data=redacted_output,
                execution_time_ms=execution_time_ms,
                trace_id=getattr(http_request.state, "trace_id", None),
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
                trace_id=getattr(http_request.state, "trace_id", None),
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
                input_data=tool_request.input_data,
                output_data=None,
                execution_time_ms=execution_time_ms,
                trace_id=getattr(http_request.state, "trace_id", None),
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
        from tenure_mcp.langgraphs.executor import get_workflow_executor

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

            elif workflow_name == "unified_collection":
                property_id = body.get("property_id")
                if not property_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Missing property_id",
                    )
                collection_scope = body.get("collection_scope")  # Optional
                result = await executor.execute_unified_collection(
                    property_id, context, collection_scope
                )

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

    # Query agent endpoint (variable input, LLM + tools including web search)
    @app.post(f"/{settings.mcp_api_version}/agent/query")
    async def agent_query(
        body: AgentQueryInput,
        user_id: str = Header(..., alias="X-User-ID"),
        tenant_id: str = Header(..., alias="X-Tenant-ID"),
        auth_context: str = Header(..., alias="X-Auth-Context"),
        role: str = Header(default="agent", alias="X-Role"),
    ):
        """Run the query agent: natural language query, returns answer and tool calls used."""
        context = RequestContext(
            user_id=user_id,
            tenant_id=tenant_id,
            auth_context=auth_context,
            role=role,
        )
        policy_gateway = get_policy_gateway()
        context_valid, context_error = policy_gateway.check_request_context(context)
        if not context_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=context_error,
            )
        try:
            result = await execute_query_agent(
                query=body.query,
                context=context,
                max_steps=body.max_steps,
            )
            return result
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Agent query failed: {str(e)}",
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
