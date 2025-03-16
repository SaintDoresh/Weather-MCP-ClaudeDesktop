from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP
import asyncio
import logging
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("weather-mcp")

# API Key from environment variables
API_KEY = os.getenv("OPENWEATHER_API_KEY")
if not API_KEY:
    logger.warning("OpenWeather API key not found in environment variables. Please set OPENWEATHER_API_KEY in your .env file.")

BASE_URL = "https://api.openweathermap.org/data/2.5"
GEO_URL = "https://api.openweathermap.org/geo/1.0"

@mcp.tool("get_current_weather")
async def get_current_weather(location: str) -> Dict[str, Any]:
    """Get current weather conditions for a location.
    
    Args:
        location (str): City name, state code (optional), country code (optional)
                       e.g., "London", "New York,US", "Paris,FR"
    
    Returns:
        Dict containing current weather data
    """
    try:
        if not API_KEY:
            return {"error": "OpenWeather API key not configured. Please set OPENWEATHER_API_KEY in your .env file."}
            
        # Get coordinates using geocoding API
        geo_response = requests.get(f"{GEO_URL}/direct?q={location}&limit=1&appid={API_KEY}")
        geo_data = geo_response.json()
        
        # Check for API errors
        if isinstance(geo_data, dict) and geo_data.get('cod') in [401, '401']:
            return {"error": f"API Key error: {geo_data.get('message', 'Invalid API key')}"}
        
        if not geo_data or len(geo_data) == 0:
            return {"error": f"Location '{location}' not found"}
        
        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]
        place_name = geo_data[0]["name"]
        country = geo_data[0].get("country", "")
        
        # Get current weather data
        weather_response = requests.get(
            f"{BASE_URL}/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        )
        weather_data = weather_response.json()
        
        if weather_response.status_code != 200:
            return {"error": f"Weather data not available: {weather_data.get('message', 'Unknown error')}"}
            
        weather = {
            "location": {
                "name": place_name,
                "country": country,
                "lat": lat,
                "lon": lon
            },
            "temperature": {
                "current": weather_data["main"]["temp"],
                "feels_like": weather_data["main"]["feels_like"],
                "min": weather_data["main"]["temp_min"],
                "max": weather_data["main"]["temp_max"]
            },
            "weather_condition": {
                "main": weather_data["weather"][0]["main"],
                "description": weather_data["weather"][0]["description"],
                "icon": weather_data["weather"][0]["icon"]
            },
            "wind": {
                "speed": weather_data["wind"]["speed"],
                "deg": weather_data["wind"]["deg"]
            },
            "clouds": weather_data["clouds"]["all"],
            "humidity": weather_data["main"]["humidity"],
            "pressure": weather_data["main"]["pressure"],
            "visibility": weather_data.get("visibility", 0),
            "sunrise": datetime.fromtimestamp(weather_data["sys"]["sunrise"]).isoformat(),
            "sunset": datetime.fromtimestamp(weather_data["sys"]["sunset"]).isoformat(),
            "timestamp": datetime.fromtimestamp(weather_data["dt"]).isoformat()
        }
        
        return weather
    except Exception as e:
        logger.error(f"Error fetching current weather for {location}: {str(e)}")
        return {"error": f"Failed to fetch current weather for {location}: {str(e)}"}

@mcp.tool("get_weather_forecast")
async def get_weather_forecast(location: str, days: int = 5) -> Dict[str, Any]:
    """Get weather forecast for a location.
    
    Args:
        location (str): City name, state code (optional), country code (optional)
                       e.g., "London", "New York,US", "Paris,FR"
        days (int): Number of days for forecast (1-5)
    
    Returns:
        Dict containing forecast data
    """
    try:
        if not API_KEY:
            return {"error": "OpenWeather API key not configured. Please set OPENWEATHER_API_KEY in your .env file."}
            
        # Limit days to valid range
        days = max(1, min(5, days))
        
        # Get coordinates using geocoding API
        geo_response = requests.get(f"{GEO_URL}/direct?q={location}&limit=1&appid={API_KEY}")
        geo_data = geo_response.json()
        
        # Check for API errors
        if isinstance(geo_data, dict) and geo_data.get('cod') in [401, '401']:
            return {"error": f"API Key error: {geo_data.get('message', 'Invalid API key')}"}
        
        if not geo_data or len(geo_data) == 0:
            return {"error": f"Location '{location}' not found"}
        
        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]
        place_name = geo_data[0]["name"]
        country = geo_data[0].get("country", "")
        
        # Get forecast data
        forecast_response = requests.get(
            f"{BASE_URL}/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&cnt={days*8}"
        )
        forecast_data = forecast_response.json()
        
        if forecast_response.status_code != 200:
            return {"error": f"Forecast data not available: {forecast_data.get('message', 'Unknown error')}"}
            
        forecast_list = forecast_data["list"]
        
        # Process forecast data
        forecast_items = []
        for item in forecast_list:
            forecast_items.append({
                "datetime": datetime.fromtimestamp(item["dt"]).isoformat(),
                "temperature": {
                    "temp": item["main"]["temp"],
                    "feels_like": item["main"]["feels_like"],
                    "min": item["main"]["temp_min"],
                    "max": item["main"]["temp_max"]
                },
                "weather_condition": {
                    "main": item["weather"][0]["main"],
                    "description": item["weather"][0]["description"],
                    "icon": item["weather"][0]["icon"]
                },
                "wind": {
                    "speed": item["wind"]["speed"],
                    "deg": item["wind"]["deg"]
                },
                "clouds": item["clouds"]["all"],
                "humidity": item["main"]["humidity"],
                "pressure": item["main"]["pressure"],
                "visibility": item.get("visibility", 0),
                "pop": item.get("pop", 0)  # Probability of precipitation
            })
        
        return {
            "location": {
                "name": place_name,
                "country": country,
                "lat": lat,
                "lon": lon
            },
            "forecast": forecast_items,
            "days": days
        }
    except Exception as e:
        logger.error(f"Error fetching forecast for {location}: {str(e)}")
        return {"error": f"Failed to fetch forecast for {location}: {str(e)}"}

@mcp.tool("get_air_quality")
async def get_air_quality(location: str) -> Dict[str, Any]:
    """Get air quality data for a location.
    
    Args:
        location (str): City name, state code (optional), country code (optional)
                       e.g., "London", "New York,US", "Paris,FR"
    
    Returns:
        Dict containing air quality data
    """
    try:
        if not API_KEY:
            return {"error": "OpenWeather API key not configured. Please set OPENWEATHER_API_KEY in your .env file."}
            
        # Get coordinates using geocoding API
        geo_response = requests.get(f"{GEO_URL}/direct?q={location}&limit=1&appid={API_KEY}")
        geo_data = geo_response.json()
        
        # Check for API errors
        if isinstance(geo_data, dict) and geo_data.get('cod') in [401, '401']:
            return {"error": f"API Key error: {geo_data.get('message', 'Invalid API key')}"}
        
        if not geo_data or len(geo_data) == 0:
            return {"error": f"Location '{location}' not found"}
        
        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]
        place_name = geo_data[0]["name"]
        country = geo_data[0].get("country", "")
        
        # Get air quality data
        air_response = requests.get(
            f"{BASE_URL}/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
        )
        air_data = air_response.json()
        
        if air_response.status_code != 200:
            return {"error": f"Air quality data not available: {air_data.get('message', 'Unknown error')}"}
            
        aqi_levels = {
            1: "Good",
            2: "Fair",
            3: "Moderate",
            4: "Poor",
            5: "Very Poor"
        }
        
        components = air_data["list"][0]["components"]
        aqi = air_data["list"][0]["main"]["aqi"]
            
        return {
            "location": {
                "name": place_name,
                "country": country,
                "lat": lat,
                "lon": lon
            },
            "air_quality_index": aqi,
            "air_quality_level": aqi_levels.get(aqi, "Unknown"),
            "components": {
                "co": components.get("co", 0),       # Carbon monoxide
                "no": components.get("no", 0),       # Nitrogen monoxide
                "no2": components.get("no2", 0),     # Nitrogen dioxide
                "o3": components.get("o3", 0),       # Ozone
                "so2": components.get("so2", 0),     # Sulphur dioxide
                "pm2_5": components.get("pm2_5", 0), # Fine particles matter
                "pm10": components.get("pm10", 0),   # Coarse particulate matter
                "nh3": components.get("nh3", 0)      # Ammonia
            },
            "timestamp": datetime.fromtimestamp(air_data["list"][0]["dt"]).isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching air quality for {location}: {str(e)}")
        return {"error": f"Failed to fetch air quality for {location}: {str(e)}"}

@mcp.tool("get_historical_weather")
async def get_historical_weather(location: str, date: str) -> Dict[str, Any]:
    """Get historical weather data for a specific date.
    
    Args:
        location (str): City name, state code (optional), country code (optional)
                       e.g., "London", "New York,US", "Paris,FR"
        date (str): Date in YYYY-MM-DD format (must be within last 5 days)
    
    Returns:
        Dict containing historical weather data
    """
    try:
        if not API_KEY:
            return {"error": "OpenWeather API key not configured. Please set OPENWEATHER_API_KEY in your .env file."}
            
        # Validate date format
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            
            # Check if date is within allowed range (last 5 days)
            days_diff = (datetime.now() - date_obj).days
            if days_diff < 0 or days_diff > 5:
                return {"error": "Historical data is only available for the last 5 days"}
                
        except ValueError:
            return {"error": "Invalid date format. Please use YYYY-MM-DD"}
        
        # Get coordinates using geocoding API
        geo_response = requests.get(f"{GEO_URL}/direct?q={location}&limit=1&appid={API_KEY}")
        geo_data = geo_response.json()
        
        # Check for API errors
        if isinstance(geo_data, dict) and geo_data.get('cod') in [401, '401']:
            return {"error": f"API Key error: {geo_data.get('message', 'Invalid API key')}"}
        
        if not geo_data or len(geo_data) == 0:
            return {"error": f"Location '{location}' not found"}
        
        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]
        place_name = geo_data[0]["name"]
        country = geo_data[0].get("country", "")
        
        # Convert date to unix timestamp
        timestamp = int(date_obj.timestamp())
        
        # Get historical weather data
        historical_response = requests.get(
            f"{BASE_URL}/onecall/timemachine?lat={lat}&lon={lon}&dt={timestamp}&appid={API_KEY}&units=metric"
        )
        historical_data = historical_response.json()
        
        if historical_response.status_code != 200:
            return {"error": f"Historical data not available: {historical_data.get('message', 'Unknown error')}"}
            
        data = historical_data["data"][0]
            
        return {
            "location": {
                "name": place_name,
                "country": country,
                "lat": lat,
                "lon": lon
            },
            "date": date,
            "temperature": {
                "temp": data["temp"],
                "feels_like": data["feels_like"]
            },
            "weather_condition": {
                "main": data["weather"][0]["main"],
                "description": data["weather"][0]["description"],
                "icon": data["weather"][0]["icon"]
            },
            "wind": {
                "speed": data["wind_speed"],
                "deg": data["wind_deg"]
            },
            "clouds": data["clouds"],
            "humidity": data["humidity"],
            "pressure": data["pressure"],
            "visibility": data.get("visibility", 0),
            "sunrise": datetime.fromtimestamp(data["sunrise"]).isoformat(),
            "sunset": datetime.fromtimestamp(data["sunset"]).isoformat(),
            "timestamp": datetime.fromtimestamp(data["dt"]).isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching historical weather for {location} on {date}: {str(e)}")
        return {"error": f"Failed to fetch historical weather: {str(e)}"}

@mcp.tool("search_location")
async def search_location(query: str) -> Dict[str, Any]:
    """Search for locations by name.
    
    Args:
        query (str): Search term (city name, etc.)
    
    Returns:
        Dict containing search results
    """
    try:
        if not API_KEY:
            return {"error": "OpenWeather API key not configured. Please set OPENWEATHER_API_KEY in your .env file."}
            
        # Get locations using geocoding API
        geo_response = requests.get(f"{GEO_URL}/direct?q={query}&limit=5&appid={API_KEY}")
        geo_data = geo_response.json()
        
        # Check for API errors
        if isinstance(geo_data, dict) and geo_data.get('cod') in [401, '401']:
            return {"error": f"API Key error: {geo_data.get('message', 'Invalid API key')}"}
        
        if not geo_data or len(geo_data) == 0:
            return {"error": f"No locations found for '{query}'"}
        
        locations = []
        for location in geo_data:
            locations.append({
                "name": location["name"],
                "state": location.get("state", ""),
                "country": location.get("country", ""),
                "lat": location["lat"],
                "lon": location["lon"]
            })
            
        return {"results": locations}
    except Exception as e:
        logger.error(f"Error searching for location '{query}': {str(e)}")
        return {"error": f"Search failed: {str(e)}"}

@mcp.tool("get_weather_alerts")
async def get_weather_alerts(location: str) -> Dict[str, Any]:
    """Get weather alerts for a location.
    
    Args:
        location (str): City name, state code (optional), country code (optional)
                       e.g., "London", "New York,US", "Paris,FR"
    
    Returns:
        Dict containing weather alerts
    """
    try:
        if not API_KEY:
            return {"error": "OpenWeather API key not configured. Please set OPENWEATHER_API_KEY in your .env file."}
            
        # Get coordinates using geocoding API
        geo_response = requests.get(f"{GEO_URL}/direct?q={location}&limit=1&appid={API_KEY}")
        geo_data = geo_response.json()
        
        # Check for API errors
        if isinstance(geo_data, dict) and geo_data.get('cod') in [401, '401']:
            return {"error": f"API Key error: {geo_data.get('message', 'Invalid API key')}"}
        
        if not geo_data or len(geo_data) == 0:
            return {"error": f"Location '{location}' not found"}
        
        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]
        place_name = geo_data[0]["name"]
        country = geo_data[0].get("country", "")
        
        # Get one call data which includes alerts
        onecall_response = requests.get(
            f"{BASE_URL}/onecall?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&exclude=minutely,hourly,daily"
        )
        onecall_data = onecall_response.json()
        
        if onecall_response.status_code != 200:
            return {"error": f"Weather alerts not available: {onecall_data.get('message', 'Unknown error')}"}
            
        alerts = onecall_data.get("alerts", [])
        alerts_data = []
        
        for alert in alerts:
            alerts_data.append({
                "sender": alert.get("sender_name", "Unknown source"),
                "event": alert.get("event", "Unknown event"),
                "start": datetime.fromtimestamp(alert.get("start", 0)).isoformat(),
                "end": datetime.fromtimestamp(alert.get("end", 0)).isoformat(),
                "description": alert.get("description", "No description available"),
                "tags": alert.get("tags", [])
            })
            
        return {
            "location": {
                "name": place_name,
                "country": country,
                "lat": lat,
                "lon": lon
            },
            "alerts": alerts_data,
            "alert_count": len(alerts_data)
        }
    except Exception as e:
        logger.error(f"Error fetching weather alerts for {location}: {str(e)}")
        return {"error": f"Failed to fetch weather alerts: {str(e)}"}

if __name__ == "__main__":
    # Print API key status (without revealing the key)
    if API_KEY:
        logger.info("OpenWeather API key loaded successfully")
    else:
        logger.warning("OpenWeather API key not found. Please set OPENWEATHER_API_KEY in your .env file.")
    
    # Run the MCP server
    mcp.run()