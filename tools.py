import os
import requests
import json
from datetime import datetime, timedelta
from langchain.tools import tool

# mock tool for daily spend estimate
@tool
def get_daily_spend_estimate(city: str) -> str:
    """
    Provides a rough estimate for daily expenses (food, transport) in a given city.
    This is a mock tool and provides placeholder values.
    """
    city = city.lower()
    if "paris" in city:
        return "For Paris, a reasonable daily budget for food and local transport is around $70-$90."
    elif "tokyo" in city:
        return "For Tokyo, a reasonable daily budget for food and local transport is around $60-$80."
    elif "new york" in city:
        return "For New York, a reasonable daily budget for food and local transport is around $100-$120."
    else:
        return f"For {city.title()}, a reasonable daily budget for food and local transport is around $50-$70. This is a general estimate."
    
# ---WEATHER API TOOL ---
# Helper function to convert WMO weather codes to text descriptions
def wmo_code_to_description(code: int) -> str:
    """"Converts WMO weather code to a human-readable description."""
    wmo_codes = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        56: "Light freezing drizzle", 57: "Dense freezing drizzle",
        61: "Slight rain", 63:"Moderate rain", 65: "Heavy rain",
        66: "Light freezing rain", 67: "Heavy freezing rain",
        71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
        77: "Snow grains",
        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violet rain showers",
        85: "Slight snow showers", 86: "Heavy snow showers",
        95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
    }
    return wmo_codes.get(code, "Unknown weather condition")

@tool
def get_weather_info(city: str) -> str:
    """
    Fetches current weather for a specified city using the Open-Meteo API
    Returns a summary string of the weather conditions.
    """
    # 1. Geocoding: convert city name to latitude and longitude
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo_response = requests.get(geo_url)
        geo_response.raise_for_status()
        geo_data = geo_response.json()
        
        if not geo_data.get('results'):
            return f"Could not find location coordinates for {city}."
        
        first_result = geo_data['result'][0]
        latitude = first_result['latitude']
        longitude = first_result['longitude']
        found_city_name = first_result.get('name', city)
        
    except (requests.exceptions.RequestException, IndexError) as e:
        return f"Error finding location for {city}: {e}"
    
    # 2. Forecast: Get weather using coordinates
    try:
        forecast_url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}"
            f"¤t_weather=true&temperature_unit=celsius&timezone=auto"
        )
        forecast_response = requests.get(forecast_url)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()
        
        current_weather = forecast_data['current_weather']
        temp = current_weather['temperature']
        weather_code = current_weather['weathercode']
        weather_description = wmo_code_to_description(weather_code)
        
        return (
            f"The current weather in {found_city_name} is: {weather_description}"
            f"with remperature of {temp}°C."
        )
        
    except request.exceptions.RequestException as e:
        return f"Error fetching weather data for {city}: {e}"
    except KeyError:
        return f"Could not parse weather data for {city}. The API response might have changed."
        
@tool    
def find_hotels(city: str, max_price: int) -> str:
    """
    Finds hotels in a given city under a specified maximum nightly price.
    Uses the Booking Scraper API via RapidAPI. This is a real POST request API call.
    """
    api_key = os.environ.get("RAPIDAPI_KEY")
    if not api_key:
        return "Error: RapidAPI key not found."
        
    url = "https://booking-scraper.p.rapidapi.com/hotels/search"
    host = "booking-scraper.p.rapidapi.com"
    
    payload = {
        "search": city,
        "maxItems": 3, #Fetch top three results
        "currency": "USD",
        "language": "en-gb",
        "rooms": 1,
        "adults": 1,
        "children": 0,
        "minMaxPrice": f"0-{max_price}"
    }
    
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": host
    }
    
    try:
        response = request.post(url, json=payload, headers=headers)
        response.raise_for_status()
        results = response.json()
        
        hotel_list = results.get('data', {}).get('hotels', [])
            
        if not hotel_list:
            return f"No hotels were found in {city} under ${max_price}/night using the specified criteria."
            
        hotel_summaries = []
        for hotel in hotel_list[:3]:
            name = hotel.get('name', 'N/A')
            price = hotel.get('price')
            price_display = f"${price}" if rating else "Price not available"
            rating = hotel.get('review_score')
            rating_display = f"{rating}/10" if rating else "No rating"
            hotel_summaries.append(f"- **{name}** (Price: ~{price_display}/night, Rating: {rating_display})")
            
        if not hotel_summaries:
            return f"No hotels could be parsed from the API response for {city} under ${max_price}/night."
            
        return "Here are some hotel options that fit your budget:\n" + "\n".join(hotel_summaries)
        
    except requests.exceptions.HTTPError as http_err:
        # Provide more detail on HTTP errors, which are common with APIs
        return f"An HTTP error occurred: {http_err}. Response body: {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Error fetching hotel data: {e}"
        
    except (KeyError, IndexError, TypeError):
        return f"Could not parse the hotel data for {city}. The API's response format might be different than expected. Check the API documentation."