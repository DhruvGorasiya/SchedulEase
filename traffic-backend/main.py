import googlemaps
import json
import time
from datetime import datetime, timedelta
from fastapi import FastAPI

# Set up FastAPI
app = FastAPI()

# Set up your Google Maps client
gmaps = googlemaps.Client(key='GOOGLE_API_KEY') #look in whatsapp for key

# Function to get public transport locations in a city
def get_transport_locations(city_name):
    geocode_result = gmaps.geocode(city_name)
    
    if not geocode_result:
        return f"City '{city_name}' not found."

    city_location = geocode_result[0]['geometry']['location']
    lat, lng = city_location['lat'], city_location['lng']

    transport_types = ['train_station', 'airport']
    transport_locations = []

    for transport_type in transport_types:
        places_result = gmaps.places_nearby((lat, lng), radius=5000, type=transport_type)
        
        for place in places_result.get('results', []):
            transport_locations.append(place['name'] + ', ' + city_name)
    
    return transport_locations

@app.get("/traffic")
def get_traffic_data(city_name: str, destination: str, future_date: str):
    start_time = datetime.strptime(future_date, "%Y-%m-%d")
    data_collection = {}
    transport_locations = get_transport_locations(city_name)[:25]  # Limit to 25 origins
    
    commute_time_sums = {location: 0 for location in transport_locations}
    count_entries = {location: 0 for location in transport_locations}
    
    # Loop from 9 AM to midnight
    for hour in range(9, 24):
        current_time = start_time + timedelta(hours=hour)
        unix_timestamp = int(time.mktime(current_time.timetuple()))
        
        traffic_results = gmaps.distance_matrix(
            origins=transport_locations,
            destinations=[destination],
            departure_time=unix_timestamp,
            traffic_model="best_guess",
            mode="driving"
        )
        
        for j, origin in enumerate(transport_locations):
            duration_text = traffic_results["rows"][j]["elements"][0].get("duration_in_traffic", {}).get("text", "N/A")
            duration_value = traffic_results["rows"][j]["elements"][0].get("duration_in_traffic", {}).get("value", None)
            
            if origin not in data_collection:
                data_collection[origin] = {"times": {}}
            
            data_collection[origin]["times"][current_time.strftime("%H:%M")] = {
                "travel_time_text": duration_text,
                "travel_time_seconds": duration_value
            }
            
            if duration_value:
                commute_time_sums[origin] += duration_value
                count_entries[origin] += 1
    
    # Calculate average commute times
    average_times = {}
    for origin in transport_locations:
        if count_entries[origin] > 0:
            average_times[origin] = {"average_commute_time": commute_time_sums[origin] / count_entries[origin]}
        else:
            average_times[origin] = {"average_commute_time": 0}
    
    return {"traffic_data": data_collection, "average_times": average_times}