# Weather Microservice App

Simple gRPC + FastAPI weather microservice that fetches live weather from OpenWeather, stores history in MongoDB, and exposes a small React UI.

What it does
- Fetches current weather for a requested city from OpenWeather and returns it over gRPC.
- Persists successful fetches to MongoDB so you can review a history of queries.
- Exposes a small FastAPI REST layer for simple HTTP-based access and a Vite/React frontend to visualize history and trends (temperature, humidity, wind).
- Includes a small CLI client to query the gRPC API from the terminal.

Features
- gRPC Weather service (protected by an `x-api-key` header)
- OpenWeather provider for live weather
- MongoDB repository to persist history
- FastAPI REST frontend wrapping the gRPC service
- React + Vite UI showing current weather, history, and trends (temperature / humidity / wind)
- CLI client for quick lookups

Requirements
- Python 3.11+
- Node.js (for the frontend) and npm
- MongoDB (or use mongomock for unit tests)

Quick start (development)
1. Create a Python virtual environment and activate it (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Install frontend deps and run Vite (in a separate shell):

```powershell
cd weather-ui
npm install
npm run dev
```

4. Start MongoDB (local or Docker), then run the gRPC server or use docker-compose to run everything:

```powershell
# using docker-compose
docker compose up --build

# or run server locally
python -m weather_service.server.weather_server
```

Setting `OPENWEATHER_API_KEY` in your venv (PowerShell)

The server needs an OpenWeather API key to fetch live data. Do NOT commit the key to source control. Set it in your shell (example uses placeholders):

```powershell
# inside your activated venv PowerShell session
$env:OPENWEATHER_API_KEY = '<your_openweather_api_key_here>'
$env:GRPC_API_KEY = '<your_grpc_api_key_here>'
# optional: set Mongo connection and server host/port too
$env:MONGO_URI = 'mongodb://localhost:27017'
$env:MONGO_DB = 'weather_db'
$env:MONGO_COLLECTION = 'weather'

# then run the server
python -m weather_service.server.weather_server
```

CLI usage
The repository includes a small gRPC CLI client at `weather_service/client/client.py`. It accepts a city name and optional flags:

```powershell
# Example: query London using default host/port and API key from env
python -m weather_service.client.client London

# Specify host/port and API key manually
python -m weather_service.client.client London --host localhost --port 50051 --api-key secret123
```

Notes
- The project contains unit tests under `weather_service/**/unit_tests` and uses `mongomock` for repository tests so MongoDB is not required for unit testing.
- The frontend build uses Vite. If your docker build fails due to Node/Vite issues, run the frontend build locally (`cd weather-ui && npm ci && npm run build`) to diagnose.
- For production, do not store secrets in `.env` in the repo — use a secrets manager or Docker secrets.

Contributing
- Run tests:

```powershell
python -m pytest -q
```


