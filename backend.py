import socketio
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import uvicorn
from datetime import datetime, timedelta
import pandas as pd
import os

app = FastAPI()

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Jinja2 template engine
templates = Jinja2Templates(directory="templates")

# Create a SocketIO server instance
sio = socketio.AsyncServer(async_mode='asgi')
sio_app = socketio.ASGIApp(sio)

# Mount Socket.IO app
app.mount("/socket.io", sio_app)

def load_data(requested_date=None):
    """Load wildfire and weather data from CSV files for the requested date"""
    try:
        if requested_date is not None:
            requested_date = pd.to_datetime(requested_date).date()
        
        if requested_date and requested_date <= datetime(2021, 1, 1).date():
            year = requested_date.year
            file_path = f'static/output_by_year/merged_data_{year}.csv'
        
            if not os.path.exists(file_path):
                print(f"Warning: No data file found for year {year} at {file_path}")
                return []
        else:
            file_path = 'static/predicted_fire_sizes.csv'

        if not os.path.exists(file_path):
            print(f"Error: File not found at {file_path}")
            return []
            
        # Read the Data
        df = pd.read_csv(file_path)

        # Convert date column to datetime and extract only the date part
        df['date'] = pd.to_datetime(df['date']).dt.date
        df = df[df['fire_size'] >= 0]
        # Convert requested date to date only (remove time component)
        if requested_date is not None:
            requested_date = pd.to_datetime(requested_date).date()
        
        # Filter for the specific date
        df_filtered = df[df['date'] == requested_date]
        
        if len(df_filtered) == 0:
            print(f"No records found for {requested_date}")
            return []
        print(df_filtered.head())
        # Convert to list of dictionaries with required format
        data = []
        for _, row in df_filtered.iterrows():
            data.append({
                'fips': row['fips'],
                'fire_size': row['fire_size'],
                'LATITUDE': row['lat'],
                'LONGITUDE': row['lon'],
                'fmc': row['fmc'],
                'tmax': row['tmax'],
                'tmin': row['tmin'],
                'prcp': row['prcp'],
                'wind_speed': row['wind_speed'],
            })
        
        return data
        
    except Exception as e:
        print(f"Error loading wildfire data: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return []

# Socket.IO events
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    await sio.send(sid, "Welcome to the server!")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.event
async def data_request(sid, data):
    print(f"\n--- Received data request from client {sid} ---")
    print(f"Received data: {data}")
    
    try:
        timestamp = data.get('time')

        # Convert timestamp to datetime
        date = datetime.fromtimestamp(timestamp)

        # Load wildfire data for the requested date
        wildfire_data = load_data(date)
        print(f"Loaded {len(wildfire_data)} wildfire records")
        if wildfire_data:
            print(f"Sample wildfire record: {wildfire_data[0]}")
        
        response = {
            "wildfire": wildfire_data
        }
        
        await sio.emit("data_broadcast", response, room=sid)
        
    except Exception as e:
        print(f"Error in data_request: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        # Send empty response to prevent frontend errors
        await sio.emit("data_broadcast", {
            "wildfire": [],
        }, room=sid)

# Web routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main page"""
    # Calculate today + 14 days
    max_date = datetime.now() + timedelta(days=14)
    max_date_str = max_date.strftime("%Y-%m-%d")
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        'min_year': "1992-01-01",
        'max_year': max_date_str
    })


@app.get("/report", response_class=HTMLResponse)
async def report_page(request: Request):

    prcp_avg = pd.read_csv("static/reports/avg_fire_size_prcp.csv").to_dict(orient="records")
    temp_avg = pd.read_csv("static/reports/avg_fire_size_temp.csv").to_dict(orient="records")
    prcp_fire_count = pd.read_csv("static/reports/fire_count_prcp.csv").to_dict(orient="records")
    temp_fire_count = pd.read_csv("static/reports/fire_count_temp.csv").to_dict(orient="records")

    return templates.TemplateResponse("report.html", {
        "request": request,
        "prcp_avg": prcp_avg,
        "temp_avg": temp_avg,
        "prcp_fire_count": prcp_fire_count,
        "temp_fire_count": temp_fire_count,
    })

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)