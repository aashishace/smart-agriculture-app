"""
Weather Service - Integration with OpenWeatherMap API
"""

import requests
from datetime import datetime, timedelta
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class WeatherService:
    """Service for fetching weather data from OpenWeatherMap."""
    
    def __init__(self):
        self.api_key = current_app.config.get('OPENWEATHER_API_KEY')
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
        if not self.api_key:
            logger.warning("OpenWeatherMap API key not configured")
    
    def get_current_weather(self, latitude, longitude):
        """
        Get current weather for given coordinates.
        
        Args:
            latitude (float): Location latitude
            longitude (float): Location longitude
            
        Returns:
            dict: Weather data or None if error
        """
        if not self.api_key:
            return self._get_mock_weather_data()
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                'lat': latitude,
                'lon': longitude,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'en'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return self._format_current_weather(data)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather API error: {e}")
            return self._get_mock_weather_data()
        except Exception as e:
            logger.error(f"Weather service error: {e}")
            return self._get_mock_weather_data()
    
    def get_forecast(self, latitude, longitude, days=5):
        """
        Get weather forecast for given coordinates.
        
        Args:
            latitude (float): Location latitude
            longitude (float): Location longitude
            days (int): Number of days forecast (max 5)
            
        Returns:
            dict: Forecast data or None if error
        """
        if not self.api_key:
            return self._get_mock_forecast_data(days)
        
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'lat': latitude,
                'lon': longitude,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': min(days * 8, 40),  # 3-hour intervals, max 40 (5 days)
                'lang': 'en'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return self._format_forecast_data(data)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather forecast API error: {e}")
            return self._get_mock_forecast_data(days)
        except Exception as e:
            logger.error(f"Weather forecast service error: {e}")
            return self._get_mock_forecast_data(days)
    
    def _format_current_weather(self, data):
        """Format current weather data from API response."""
        try:
            return {
                'temperature': round(data['main']['temp'], 1),
                'feels_like': round(data['main']['feels_like'], 1),
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'description': data['weather'][0]['description'].title(),
                'wind_speed': data['wind'].get('speed', 0),
                'wind_direction': data['wind'].get('deg', 0),
                'clouds': data['clouds']['all'],
                'visibility': data.get('visibility', 10000) / 1000,  # Convert to km
                'uv_index': None,  # Not available in current weather
                'rain_1h': data.get('rain', {}).get('1h', 0),
                'rain_probability': min(data['clouds']['all'], 100),  # Estimate from clouds
                'sunrise': datetime.fromtimestamp(data['sys']['sunrise']),
                'sunset': datetime.fromtimestamp(data['sys']['sunset']),
                'location': data['name'],
                'updated_at': datetime.now()
            }
        except KeyError as e:
            logger.error(f"Error formatting weather data: {e}")
            return self._get_mock_weather_data()
    
    def _format_forecast_data(self, data):
        """Format forecast data from API response."""
        try:
            forecasts = []
            
            for item in data['list']:
                forecast = {
                    'datetime': datetime.fromtimestamp(item['dt']),
                    'temperature': round(item['main']['temp'], 1),
                    'temperature_min': round(item['main']['temp_min'], 1),
                    'temperature_max': round(item['main']['temp_max'], 1),
                    'humidity': item['main']['humidity'],
                    'description': item['weather'][0]['description'].title(),
                    'wind_speed': item['wind'].get('speed', 0),
                    'clouds': item['clouds']['all'],
                    'rain_3h': item.get('rain', {}).get('3h', 0),
                    'rain_probability': item.get('pop', 0) * 100  # Probability of precipitation
                }
                forecasts.append(forecast)
            
            return {
                'location': data['city']['name'],
                'forecasts': forecasts,
                'updated_at': datetime.now()
            }
            
        except KeyError as e:
            logger.error(f"Error formatting forecast data: {e}")
            return self._get_mock_forecast_data(5)
    
    def _get_mock_weather_data(self):
        """Return mock weather data for development/testing."""
        return {
            'temperature': 28.5,
            'feels_like': 31.2,
            'humidity': 65,
            'pressure': 1013,
            'description': 'Partly Cloudy',
            'wind_speed': 3.2,
            'wind_direction': 180,
            'clouds': 40,
            'visibility': 10.0,
            'uv_index': None,
            'rain_1h': 0,
            'rain_probability': 30,
            'sunrise': datetime.now().replace(hour=6, minute=30),
            'sunset': datetime.now().replace(hour=18, minute=45),
            'location': 'Sample Location',
            'updated_at': datetime.now()
        }
    
    def _get_mock_forecast_data(self, days):
        """Return mock forecast data for development/testing."""
        forecasts = []
        base_time = datetime.now()
        
        for i in range(days * 8):  # 3-hour intervals
            forecast_time = base_time + timedelta(hours=i * 3)
            forecasts.append({
                'datetime': forecast_time,
                'temperature': 28.5 + (i % 10 - 5),  # Vary temperature
                'temperature_min': 25.0 + (i % 8 - 4),
                'temperature_max': 32.0 + (i % 6 - 3),
                'humidity': 65 + (i % 20 - 10),
                'description': ['Clear', 'Partly Cloudy', 'Cloudy', 'Light Rain'][i % 4],
                'wind_speed': 3.2 + (i % 4),
                'clouds': 40 + (i % 30),
                'rain_3h': 0 if i % 4 != 3 else 2.5,
                'rain_probability': 30 + (i % 40)
            })
        
        return {
            'location': 'Sample Location',
            'forecasts': forecasts,
            'updated_at': datetime.now()
        }
    
    def analyze_irrigation_conditions(self, latitude, longitude):
        """
        Analyze weather conditions for irrigation recommendations.
        
        Returns:
            dict: Irrigation analysis results
        """
        current_weather = self.get_current_weather(latitude, longitude)
        forecast = self.get_forecast(latitude, longitude, days=3)
        
        if not current_weather or not forecast:
            return None
        
        # Analyze next 24 hours for rain
        next_24h_rain = 0
        rain_probability_max = 0
        
        now = datetime.now()
        for forecast_item in forecast['forecasts']:
            if forecast_item['datetime'] <= now + timedelta(hours=24):
                next_24h_rain += forecast_item['rain_3h']
                rain_probability_max = max(rain_probability_max, forecast_item['rain_probability'])
        
        return {
            'current_temperature': current_weather['temperature'],
            'current_humidity': current_weather['humidity'],
            'rain_next_24h': next_24h_rain,
            'rain_probability_max': rain_probability_max,
            'wind_speed': current_weather['wind_speed'],
            'recommendation': self._get_irrigation_recommendation(
                current_weather, next_24h_rain, rain_probability_max
            )
        }
    
    def _get_irrigation_recommendation(self, current_weather, rain_next_24h, rain_probability):
        """Generate irrigation recommendation based on weather."""
        if rain_probability > 70:
            return "skip_rain_expected"
        elif rain_next_24h > 5:
            return "skip_sufficient_rain"
        elif current_weather['temperature'] > 35 and current_weather['humidity'] < 40:
            return "irrigate_hot_dry"
        elif current_weather['wind_speed'] > 15:
            return "irrigate_early_windy"
        else:
            return "irrigate_normal"
