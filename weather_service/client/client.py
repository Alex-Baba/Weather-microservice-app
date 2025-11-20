from weather_service.server.config import settings
import grpc
import argparse
import os
from generated.proto import weather_pb2, weather_pb2_grpc


def format_response(resp):
    out = []
    out.append(f"Weather for {resp.city_name}:")
    out.append(f"  Temperature: {resp.temperature} °C")
    out.append(f"  Humidity: {resp.humidity}%")
    out.append(f"  Conditions: {resp.description}")
    out.append(f"  Wind Speed: {resp.wind_speed} m/s")
    try:
        # fetched_at is a google.protobuf.Timestamp message
        if resp.HasField('fetched_at'):
            dt = resp.fetched_at.ToDatetime()
            out.append(f"  Fetched at: {dt.isoformat()}")
    except Exception:
        pass
    return "\n".join(out)


def run_cli(city: str, host: str, port: int, api_key: str, timeout: float = 10.0):
    target = f"{host}:{port}"
    channel = grpc.insecure_channel(target)
    stub = weather_pb2_grpc.WeatherServiceStub(channel)
    try:
        resp = stub.GetWeather(
            weather_pb2.WeatherRequest(city_name=city),
            metadata=(("x-api-key", api_key),) if api_key else (),
            timeout=timeout,
        )
        print(format_response(resp))
        return 0
    except grpc.RpcError as e:
        code = e.code() if hasattr(e, 'code') else None
        details = e.details() if hasattr(e, 'details') else str(e)
        print(f"RPC failed: {code} - {details}")
        return 2


def main():
    parser = argparse.ArgumentParser(description='gRPC Weather client')
    parser.add_argument('city', nargs='?', help='City name to fetch')
    parser.add_argument('--host', default=os.getenv('GRPC_HOST', 'localhost'), help='gRPC server host')
    parser.add_argument('--port', type=int, default=int(os.getenv('GRPC_PORT', '50051')), help='gRPC server port')
    parser.add_argument('--api-key', default=os.getenv('GRPC_API_KEY', settings.GRPC_API_KEY), help='API key for gRPC x-api-key metadata')
    args = parser.parse_args()

    city = args.city
    if not city:
        try:
            city = input('Enter city name: ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\nAborted')
            return 1
    if not city:
        print('No city provided')
        return 1

    return run_cli(city=city, host=args.host, port=args.port, api_key=args.api_key)


if __name__ == '__main__':
    raise SystemExit(main())