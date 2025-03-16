# Weather MCP Tool for Claude Desktop

An MCP (Model Context Protocol) tool that provides real-time weather data, forecasts, and historical weather information using the OpenWeatherMap API, specifically designed for Claude Desktop.

## Tutorial

For a detailed guide on setting up and using this tool, check out our comprehensive Medium tutorial:
[Tutorial: Using Claude Desktop with Weather MCP Tool to Access Real-Time Weather Data Worldwide](https://medium.com/@saintdoresh/tutorial-using-claude-desktop-with-weather-mcp-tool-to-access-real-time-weather-data-worldwide-a0b811fc5cdf)

## Features

- Real-time weather conditions for any location
- Weather forecasts (up to 5 days)
- Historical weather data (last 5 days)
- Air quality information
- Weather alerts and warnings
- Location search functionality

## Setup

1. Ensure you have Python 3.10 or higher installed

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Get an API key from [OpenWeatherMap](https://openweathermap.org/api) (free tier available)
   - Note: New API keys may take up to 24 hours to activate

4. Set up environment variables for API key (recommended method):
   - Create a `.env` file in the project directory
   - Add your API key to the file:
   ```
   OPENWEATHER_API_KEY=your_openweathermap_api_key
   ```
   - Add `.env` to your `.gitignore` file to prevent committing sensitive data

5. Update `main.py` to use the environment variable:
   ```python
   # Add these imports at the top
   import os
   from dotenv import load_dotenv
   
   # Load environment variables
   load_dotenv()
   
   # Replace the API_KEY line with
   API_KEY = os.getenv("OPENWEATHER_API_KEY")
   ```

## Integration with Claude Desktop

1. Configure your MCP settings in Claude Desktop by adding the following to your MCP configuration:

```json
{
  "mcpServers": {
    "weather-mcp": {
      "command": "py",
      "args": ["-3.13", "C:\\Path\\To\\Your\\Weather-MCP-ClaudeDesktop\\main.py"]
    }
  }
}
```

2. Replace the path with the full path to your main.py file
3. Run the server using:
```bash
py -3.13 main.py
```
4. Keep the server running while using Claude Desktop

## Available Tools

### 1. get_current_weather
Get real-time weather conditions for a location:
```json
{
    "location": {
        "name": "New York",
        "country": "US",
        "lat": 40.7128,
        "lon": -74.006
    },
    "temperature": {
        "current": 25.6,
        "feels_like": 26.2,
        "min": 23.4,
        "max": 27.8
    },
    "weather_condition": {
        "main": "Clear",
        "description": "clear sky",
        "icon": "01d"
    },
    "wind": {
        "speed": 3.6,
        "deg": 220
    },
    "clouds": 5,
    "humidity": 65,
    "pressure": 1015,
    "visibility": 10000,
    "sunrise": "2025-03-16T06:12:34",
    "sunset": "2025-03-16T18:04:23",
    "timestamp": "2025-03-16T14:30:00"
}
```

### 2. get_weather_forecast
Get weather forecast for a location:
```json
{
    "location": {
        "name": "London",
        "country": "GB",
        "lat": 51.5074,
        "lon": -0.1278
    },
    "forecast": [
        {
            "datetime": "2025-03-16T15:00:00",
            "temperature": {
                "temp": 18.2,
                "feels_like": 17.8,
                "min": 17.5,
                "max": 19.1
            },
            "weather_condition": {
                "main": "Rain",
                "description": "light rain",
                "icon": "10d"
            },
            "wind": {
                "speed": 4.2,
                "deg": 180
            },
            "clouds": 75,
            "humidity": 82,
            "pressure": 1010,
            "visibility": 8000,
            "pop": 0.4
        }
        // ... more forecast items
    ],
    "days": 5
}
```

### 3. get_air_quality
Get air quality data for a location:
```json
{
    "location": {
        "name": "Beijing",
        "country": "CN",
        "lat": 39.9042,
        "lon": 116.4074
    },
    "air_quality_index": 3,
    "air_quality_level": "Moderate",
    "components": {
        "co": 250.34,
        "no": 0.5,
        "no2": 15.2,
        "o3": 140.8,
        "so2": 5.1,
        "pm2_5": 8.2,
        "pm10": 12.3,
        "nh3": 0.7
    },
    "timestamp": "2025-03-16T14:30:00"
}
```

### 4. get_historical_weather
Get historical weather data for a specific date:
```json
{
    "location": {
        "name": "Paris",
        "country": "FR",
        "lat": 48.8566,
        "lon": 2.3522
    },
    "date": "2025-03-14",
    "temperature": {
        "temp": 20.3,
        "feels_like": 19.8
    },
    "weather_condition": {
        "main": "Clouds",
        "description": "scattered clouds",
        "icon": "03d"
    },
    "wind": {
        "speed": 2.8,
        "deg": 150
    },
    "clouds": 45,
    "humidity": 60,
    "pressure": 1012,
    "visibility": 10000,
    "sunrise": "2025-03-14T06:30:45",
    "sunset": "2025-03-14T18:15:22",
    "timestamp": "2025-03-14T12:00:00"
}
```

### 5. search_location
Search for locations by name:
```json
{
    "results": [
        {
            "name": "Tokyo",
            "state": "",
            "country": "JP",
            "lat": 35.6762,
            "lon": 139.6503
        },
        {
            "name": "Tokyo",
            "state": "Tokyo",
            "country": "JP",
            "lat": 35.6895,
            "lon": 139.6917
        }
        // ... more results
    ]
}
```

### 6. get_weather_alerts
Get weather alerts for a location:
```json
{
    "location": {
        "name": "Miami",
        "country": "US",
        "lat": 25.7617,
        "lon": -80.1918
    },
    "alerts": [
        {
            "sender": "NWS Miami",
            "event": "Heat Advisory",
            "start": "2025-03-16T12:00:00",
            "end": "2025-03-16T20:00:00",
            "description": "Heat index values between 105 and 110 expected",
            "tags": ["Extreme temperature value"]
        }
        // ... more alerts if any
    ],
    "alert_count": 1
}
```

## Sample Queries

You can ask Claude Desktop questions like:
- "What's the current weather in New York?"
- "Show me the 5-day forecast for London"
- "What's the air quality like in Beijing today?"
- "How was the weather in Paris on March 14th?"
- "Search for locations named 'Tokyo'"
- "Are there any weather alerts for Miami?"
- "Compare the current weather in Chicago, Miami, and Seattle"
- "Show me a comparison of air quality in Beijing, Los Angeles, and Delhi"

## Error Handling

All tools include proper error handling and will return an error message if something goes wrong:
```json
{
    "error": "Failed to fetch current weather for InvalidLocation: Location not found"
}
```

## Troubleshooting

If the MCP server is not working in Claude Desktop:
1. Make sure the server is running - you should see output when you start the script
2. Verify the path in your settings is correct and absolute
3. Make sure Python 3.10+ is in your system PATH
4. Check that all dependencies are installed
5. Try restarting Claude Desktop
6. Check logs for any error messages

### Common API Issues
- **API Key Activation**: New OpenWeatherMap API keys may take up to 24 hours to activate
- **Invalid API Key Error**: If you get a 401 error, verify your API key is correct and active
- **Rate Limiting**: Free tier allows up to 60 calls per minute, which might be exceeded during heavy usage

## Rate Limits

This tool uses the OpenWeatherMap API which has rate limits. The free tier allows up to 60 calls per minute, which should be sufficient for personal use. Please be aware that very frequent requests may be throttled by the API.

## License

MIT License