import os
import requests
import grpc
from concurrent import futures
from generated import weather_pb2, weather_pb2_grpc

OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")
GRPC_API_KEY = os.getenv("GRPC_API_KEY", "secret123")

class WeatherServicer(weather_pb2_grpc.WeatherServiceServicer):
    def GetWeather(self, request, context):
        md = dict(context.invocation_metadata())
        if md.get("x-api-key") != GRPC_API_KEY:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "invalid API key")

        city = request.city_name
        if not OPENWEATHER_KEY:
            return weather_pb2.WeatherResponse(error="Server missing OPENWEATHER_API_KEY")

        try:
            resp = requests.get(
                "http://api.openweathermap.org/data/2.5/weather",
                params={"q": city, "appid": OPENWEATHER_KEY, "units": "metric"},
                timeout=5,
            )
            resp.raise_for_status()
            data = resp.json()
            desc = (data.get("weather") or [{}])[0].get("description", "")
            temp = float(data["main"]["temp"])
            humidity = int(data["main"]["humidity"])
            wind = float(data.get("wind", {}).get("speed", 0.0))
            return weather_pb2.WeatherResponse(
                city_name=data.get("name", city),
                temperature=temp,
                humidity=humidity,
                description=desc,
                wind_speed=wind,
            )
        except requests.RequestException as e:
            return weather_pb2.WeatherResponse(error=str(e))

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    weather_pb2_grpc.add_WeatherServiceServicer_to_server(WeatherServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("gRPC server started on :50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()