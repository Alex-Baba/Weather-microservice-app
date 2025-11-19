import os
import requests
import grpc
from concurrent import futures
from generated.proto import weather_pb2, weather_pb2_grpc
from .providers.openweather import OpenWeatherProvider
from .mappers import dict_to_weather_response
from dotenv import load_dotenv

from .interceptors.api_key import ApiKeyInterceptor

load_dotenv()

OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")
GRPC_API_KEY = os.getenv("GRPC_API_KEY", "secret123")

class WeatherServicer(weather_pb2_grpc.WeatherServiceServicer):
    def GetWeather(self, request, context):
        md = dict(context.invocation_metadata())
        if md.get("x-api-key") != GRPC_API_KEY:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "invalid API key")
        city = request.city_name

        try:
            provider = OpenWeatherProvider()
        except RuntimeError:
            return weather_pb2.WeatherResponse(error="Server missing OPENWEATHER_API_KEY")

        try:
            data = provider.fetch_weather(city)
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
        except Exception as e:
            # provider may raise CityNotFoundError or ProviderError; return error message
            return weather_pb2.WeatherResponse(error=str(e))

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