import grpc
from weather_service.server.config import settings


class ApiKeyInterceptor(grpc.ServerInterceptor):
    """gRPC server interceptor that enforces an x-api-key metadata value."""

    def __init__(self, expected_key: str | None = None):
        self.expected_key = expected_key or settings.GRPC_API_KEY

    def intercept_service(self, continuation, handler_call_details):
        # handler_call_details.invocation_metadata is a sequence of MetadataTuples
        md = dict(handler_call_details.invocation_metadata or [])
        if self.expected_key and md.get("x-api-key") != self.expected_key:
            def abort_handler(request, context):
                context.abort(grpc.StatusCode.UNAUTHENTICATED, "invalid API key")

            # Return a generic handler that aborts immediately
            return grpc.unary_unary_rpc_method_handler(abort_handler)

        return continuation(handler_call_details)
