import os
import grpc
from generated.proto import weather_pb2, weather_pb2_grpc

GRPC_API_KEY = os.getenv("GRPC_API_KEY", "secret123")

def main():
    channel = grpc.insecure_channel("localhost:50051")
    stub = weather_pb2_grpc.WeatherServiceStub(channel)
    city = input("Enter city name: ").strip()
    try:
        resp = stub.GetWeather(
            weather_pb2.WeatherRequest(city_name=city),
            metadata=(("x-api-key", GRPC_API_KEY),),
            timeout=10,
        )
        if resp.error:
            print("Error:", resp.error); return
        print(f"Weather for {resp.city_name}:")
        print(f"  Temperature: {resp.temperature} °C")
        print(f"  Humidity: {resp.humidity}%")
        print(f"  Conditions: {resp.description}")
        print(f"  Wind Speed: {resp.wind_speed} m/s")
    except grpc.RpcError as e:
        print("RPC failed:", e)

if __name__ == "__main__":
    main()