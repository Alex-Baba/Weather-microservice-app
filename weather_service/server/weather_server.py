import os
import requests
import grpc
from concurrent import futures
from generated.proto import weather_pb2, weather_pb2_grpc
from .providers.openweather import OpenWeatherProvider
from .mappers import dict_to_weather_response

from weather_service.server.config import settings
from .interceptors.api_key import ApiKeyInterceptor

GRPC_API_KEY = settings.GRPC_API_KEY

class WeatherServicer(weather_pb2_grpc.WeatherServiceServicer):
    def GetWeather(self, request, context):
        md = dict(context.invocation_metadata())
        if md.get("x-api-key") != GRPC_API_KEY:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "invalid API key")
        city = request.city_name

        try:
            provider = OpenWeatherProvider()
        except RuntimeError:
            context.abort(grpc.StatusCode.INTERNAL, "Server missing OPENWEATHER_API_KEY")

        try:
            data = provider.fetch_weather(city)
        except CityNotFoundError as e:
            context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        except Exception as e:
            # ProviderError or network/parsing issues
            context.abort(grpc.StatusCode.UNAVAILABLE, str(e))

        # persist asynchronously (best-effort)
        try:
            from . import storage
            try:
                storage.save_weather(data)
            except Exception:
                pass
        except Exception:
            pass

        return dict_to_weather_response(data)

def serve():
    # attach the API key interceptor so the server rejects unauthenticated requests
    interceptor = ApiKeyInterceptor()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), interceptors=(interceptor,))
    weather_pb2_grpc.add_WeatherServiceServicer_to_server(WeatherServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("gRPC server started on :50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()