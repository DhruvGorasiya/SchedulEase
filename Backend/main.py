from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
import json
import re
import os
from openai import OpenAI
import time
from datetime import datetime, timedelta
import googlemaps
from dotenv import load_dotenv  # Import dotenv
import random

# Load environment variables
load_dotenv()

app = FastAPI()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

gmaps = googlemaps.Client(key=os.getenv('GOOGLE_API_KEY')) #look in whatsapp for key

# Clear conversations periodically (optional)
@app.on_event("startup")
async def startup_event():
    conversations.clear()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConversationState:
    def __init__(self):
        self.current_question = 0
        self.collected_data = {}
        self.questions = [
            "event_type",
            "location",
            "date",
            "time",
            "budget",
            "attendees"
        ]

class MessageRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class MessageResponse(BaseModel):
    message: str
    type: str = "question"  # can be "question", "error", "venues", or "summary"
    venues: Optional[List[dict]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class PlaceResponse(BaseModel):
    places: List[dict]
    timestamp: datetime = Field(default_factory=datetime.now)

# Store conversation states
conversations: Dict[str, ConversationState] = {}

def generate_venue_recommendations(data: dict) -> List[dict]:
    # Format the date to ensure YYYY-MM-DD format
    try:
        date_obj = datetime.strptime(data['date'], '%Y-%m-%d')
        formatted_date = date_obj.strftime('%Y-%m-%d')
    except:
        formatted_date = data['date']  # Keep original if already in correct format
    
    # Ensure event_type is single word
    event_type = data['event_type'].split()[0].lower()
    
    prompt = f"""As an expert event planner, recommend 9 real and currently operating venues in {data['location']} that would be perfect for a {event_type} with {data['attendees']} attendees and a budget of {data['budget']}.

    Research and provide real venues that actually exist, including:
    - The venue's real name and actual location
    - Their real street address
    - Actual capacity information
    - Real amenities and features they offer
    - Their genuine website or social media presence

    Format the response as a JSON object with a 'venues' array containing the recommendations.
    Example format:
    {{
        "venues": [
            {{
                "name": "Real Venue Name",
                "address": "Actual Street Address",
                "capacity": "Specific capacity range",
                "features": ["Real Feature 1", "Real Feature 2", "Real Feature 3"],
                "source": "Actual website URL",
                "state": "Actual state",
                "time": "{data['time']}",
                "date": "{formatted_date}",
                "event_type": "{event_type}",
                "budget": "{data['budget']}",
                "attendees": "{data['attendees']}",
            }}
        ]
    }}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert event planner with extensive knowledge of real venues. Always provide accurate, currently operating venues with real details."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        
        if not response.choices or not response.choices[0].message.content:
            raise Exception("No response received from OpenAI")
            
        venues_data = json.loads(response.choices[0].message.content)
        venues = venues_data.get('venues', [])
        
        # Add date and event_type to each venue
        for venue in venues:
            venue['date'] = formatted_date
            venue['event_type'] = event_type
            
        return venues
    except Exception as e:
        print(f"Error generating venues: {str(e)}")
        return [{
            "name": "Error",
            "address": "Could not generate venue recommendations at this time",
            "capacity": "Unknown",
            "features": ["Please try again later"],
            "source": "",
            "date": formatted_date,
            "event_type": event_type
        }]

def validate_input(question_type: str, user_input: str) -> tuple[bool, str]:
    """Validate user input and return (is_valid, processed_input)"""
    user_input = user_input.strip().lower()
    
    if not user_input:
        return False, "I need an answer to proceed. "
        
    if question_type == "event_type":
        if len(user_input) < 2:
            return False, "Please tell me what type of event you're planning (e.g., wedding, birthday party, conference). "
        return True, user_input
    elif question_type == "location":
        if len(user_input) < 2:
            return False, "I need a valid location to search for venues. Please provide a city name. "
        return True, user_input
    elif question_type == "date":
        try:
            # Convert common word patterns to dates
            user_input = user_input.lower()
            
            # Handle "today", "tomorrow", "day after tomorrow"
            if "today" in user_input:
                return True, datetime.now().strftime('%Y-%m-%d')
            elif "tomorrow" in user_input:
                return True, (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            elif "day after tomorrow" in user_input:
                return True, (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
            
            # Handle "next" patterns (next monday, next week, next month)
            if "next" in user_input:
                today = datetime.now()
                if "week" in user_input:
                    return True, (today + timedelta(days=7)).strftime('%Y-%m-%d')
                elif "month" in user_input:
                    # Add roughly 30 days
                    return True, (today + timedelta(days=30)).strftime('%Y-%m-%d')
                else:
                    # Try to parse day name (next monday, next tuesday, etc.)
                    for i, day in enumerate(['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']):
                        if day in user_input:
                            current_day = today.weekday()
                            target_day = i
                            days_ahead = target_day - current_day
                            if days_ahead <= 0:  # Target day has passed this week
                                days_ahead += 7
                            return True, (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
            
            # Try different date formats
            date_formats = [
                '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%m-%d-%Y', 
                '%d/%m/%y', '%m/%d/%y', '%d-%m-%y', '%m-%d-%y',
                '%B %d, %Y', '%b %d, %Y',  # December 25, 2024 or Dec 25, 2024
                '%d %B %Y', '%d %b %Y',    # 25 December 2024 or 25 Dec 2024
                '%Y-%m-%d',                # ISO format
                '%d.%m.%Y', '%m.%d.%Y',    # Dot format
                '%d %m %Y', '%m %d %Y'     # Space separated
            ]
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(user_input, fmt)
                    # Check if date is not in the past
                    if parsed_date.date() < datetime.now().date():
                        return False, "Please provide a future date. The event cannot be scheduled in the past. "
                    # Convert to YYYY-MM-DD format
                    return True, parsed_date.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            # If none of the formats match
            return False, "Please provide a valid date (e.g., DD/MM/YYYY, 'next monday', 'December 25, 2024'). "
            
        except Exception as e:
            return False, "Please provide a valid date. "
    elif question_type == "time":
        try:
            # Remove uncertainty words/phrases
            uncertainty_words = [
                'around', 'about', 'approximately', 'maybe', 'may be', 'probably',
                'likely', 'roughly', 'somewhere', 'circa', 'near', 'close to',
                'approximately at', 'at about', 'around 6pm', 'maybe noon'
            ]
            
            cleaned_input = user_input
            for word in uncertainty_words:
                cleaned_input = cleaned_input.replace(word, '').strip()
            
            # Handle special time phrases
            if "noon" in cleaned_input:
                return True, "12:00"
            elif "midnight" in cleaned_input:
                return True, "00:00"
            
            # Remove any spaces between numbers and am/pm
            cleaned_input = re.sub(r'(\d)(am|pm)', r'\1 \2', cleaned_input)
            cleaned_input = re.sub(r'(\d)([ap]\.m\.)', r'\1 \2', cleaned_input)
            
            # Handle various time formats
            time_patterns = [
                # 2:30pm, 2:30 pm, 2:30p.m., 14:30
                (r'^(\d{1,2}):(\d{2})\s*(am|pm|a\.m\.|p\.m\.)?$', 
                 lambda m: convert_to_24hr(int(m.group(1)), int(m.group(2)), m.group(3))),
                
                # 2pm, 2 pm, 2p.m., 14
                (r'^(\d{1,2})\s*(am|pm|a\.m\.|p\.m\.)?$', 
                 lambda m: convert_to_24hr(int(m.group(1)), 0, m.group(2))),
                
                # 1430, 0230 (military time)
                (r'^(\d{4})$', 
                 lambda m: f"{m.group(1)[:2]}:{m.group(1)[2:]}")
            ]
            
            for pattern, converter in time_patterns:
                match = re.match(pattern, cleaned_input)
                if match:
                    formatted_time = converter(match)
                    # Validate the time is valid
                    try:
                        datetime.strptime(formatted_time, '%H:%M')
                        return True, formatted_time
                    except ValueError:
                        continue
            
            return False, "Please provide a valid time (e.g., '2:30 PM', '14:30', 'around 6pm', 'maybe noon'). "
            
        except Exception as e:
            return False, "Please provide a valid time. "
    elif question_type == "budget":
        budget = ''.join(c for c in user_input if c.isdigit())
        if not budget:
            return False, "I need a numeric budget amount. Please provide a number. "
        return True, budget
    elif question_type == "attendees":
        attendees = ''.join(c for c in user_input if c.isdigit())
        if not attendees:
            return False, "I need a number of attendees. Please provide a numeric value. "
        return True, attendees
    
    return False, "I couldn't understand that. Please try again. "

def convert_to_24hr(hour: int, minute: int, period: str = None) -> str:
    """Convert time to 24-hour format"""
    if period:
        period = period.lower().replace('.', '')
        if period in ['pm', 'p.m'] and hour != 12:
            hour += 12
        elif period in ['am', 'a.m'] and hour == 12:
            hour = 0
    
    # Ensure valid hour
    if hour > 23:
        raise ValueError("Invalid hour")
    
    # Ensure valid minute
    if minute > 59:
        raise ValueError("Invalid minute")
        
    return f"{hour:02d}:{minute:02d}"

@app.post("/api/ai_message", response_model=MessageResponse)
async def handle_message(request: MessageRequest):
    try:
        conversation_id = request.conversation_id or "default_user"
        
        if request.message.lower() == "start":
            conversations[conversation_id] = ConversationState()
            return MessageResponse(
                message="What type of event are you planning?",
                type="question",
                timestamp=datetime.now()
            )
        
        if conversation_id not in conversations:
            conversations[conversation_id] = ConversationState()
            return MessageResponse(
                message="Please type 'start' to begin planning your event.",
                type="question",
                timestamp=datetime.now()
            )
        
        state = conversations[conversation_id]
        
        if state.current_question < len(state.questions):
            current_q = state.questions[state.current_question]
            
            is_valid, processed_input = validate_input(current_q, request.message)
            
            questions_map = {
                "event_type": "What type of event are you planning?",
                "location": "Where would you like to hold the event?",
                "date": "What date would you like to hold the event?",
                "time": "What time would you like the event to start?",
                "budget": "What's your budget for the venue?",
                "attendees": "How many people will be attending?"
            }
            
            if not is_valid:
                return MessageResponse(
                    message=f"{processed_input}{questions_map[current_q]}",
                    type="error",
                    timestamp=datetime.now()
                )
            
            state.collected_data[current_q] = processed_input
            state.current_question += 1
            
            if state.current_question < len(state.questions):
                next_q = state.questions[state.current_question]
                return MessageResponse(
                    message=questions_map[next_q],
                    type="question",
                    timestamp=datetime.now()
                )
            else:
                venues = generate_venue_recommendations(state.collected_data)
                
                # Process venues in parallel using list comprehension
                # Simplified traffic data collection
                for venue in venues:
                    try:
                        city = venue['address'].split(',')[1].strip()
                        destination = venue['name'] + ', ' + city
                        
                        # Get only essential traffic data with fewer time points
                        venue['traffic'] = get_simplified_traffic_data(city, destination, state.collected_data['date'])
                        
                        # Add other data directly without additional API calls
                        venue['accessibility_score'] = random.randint(70, 95)
                        venue['weather_data'] = predictWeather()
                        venue['safety_data'] = safetyReport()
                        
                    except Exception as e:
                        print(f"Error processing data for venue {venue.get('name')}: {str(e)}")
                        venue['traffic'] = None
                        venue['accessibility_score'] = random.randint(70, 95)
                        venue['weather_data'] = None
                        venue['safety_data'] = None
                
                try:
                    with open('event_data.json', 'a') as f:
                        json.dump(state.collected_data, f)
                        f.write('\n')
                except Exception as e:
                    print(f"Error saving to JSON: {str(e)}")
                
                del conversations[conversation_id]
                
                print(venues)
                
                return MessageResponse(
                    message="Great! I've found some venues that match your criteria.",
                    type="venues",
                    venues=venues,
                    timestamp=datetime.now()
                )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_transport_locations(city_name, airport=False):
    geocode_result = gmaps.geocode(city_name)
    
    if not geocode_result:
        return f"City '{city_name}' not found."

    city_location = geocode_result[0]['geometry']['location']
    lat, lng = city_location['lat'], city_location['lng']

    transport_types = ['train_station', 'airport'] if not airport else ['airport']
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
    airport_locations = get_transport_locations(city_name,True)[:1]
    transport_locations=get_transport_locations(city_name)[:5]

    
    # Loop from 9 AM to midnight
    for hour in range(9, 24):
        current_time = start_time + timedelta(hours=hour)
        unix_timestamp = int(time.mktime(current_time.timetuple()))
        
        traffic_results = gmaps.distance_matrix(
            origins=airport_locations,
            destinations=destination,
            departure_time=unix_timestamp,
            traffic_model="best_guess",
            mode="driving"
        )
        
        for j, origin in enumerate(airport_locations):
            duration_text = traffic_results["rows"][j]["elements"][0].get("duration_in_traffic", {}).get("text", "N/A")
            duration_value = traffic_results["rows"][j]["elements"][0].get("duration_in_traffic", {}).get("value", None)
            
            if origin not in data_collection:
                data_collection[origin] = {"times": {}}
            
            data_collection[origin]["times"][current_time.strftime("%H:%M")] = {
                "travel_time_text": duration_text,
                "travel_time_seconds": duration_value
            }
            
    # Calculate average commute times for all 5 locations
    average_times = {}
    for origin in transport_locations:
        traffic_results = gmaps.distance_matrix(
            origins=[origin],
            destinations=[destination],
            departure_time=start_time.timestamp(),
            traffic_model="best_guess",
            mode="driving"
        )
        
        duration_value = traffic_results["rows"][0]["elements"][0].get("duration_in_traffic", {}).get("value", None)
        
        if duration_value:
            average_times[origin] = {"average_commute_time": duration_value}
        else:
            average_times[origin] = {"average_commute_time": 0}
    
    return {"traffic_data": data_collection, "average_times": average_times}

# Define the input data model
class VenueFeatures(BaseModel):
    venue_name: str
    ramp_availability: str
    elevator_availability: str
    accessible_toilets: str
    wifi_availability: str
    parking_availability: str
    signage: str
    staff_assistance: str
    door_width: int
    lighting: str
    noise_level: str

# # Load the model and preprocess data when the app starts
# data = preprocess_data("data/mock_venue_accessibility_data.csv")
# model = train_model(data)

# # Define the /predict-accessibility-score endpoint
# @app.post("/predict-accessibility-score")
# def predict(features: VenueFeatures):
#     try:
#         # Convert input data to a dictionary
#         input_data = features.dict()
        
#         # Make a prediction
#         prediction = predict_accessibility_score(model, input_data)
        
#         # Clean the prediction (remove newlines, spaces, etc.)
#         prediction = prediction.strip()  # Remove leading/trailing whitespace
#         prediction = "".join(prediction.split())  # Remove all whitespace
        
#         # Convert the prediction to a float or int
#         try:
#             score = float(prediction)  # Convert to float
#             if score.is_integer():  # Check if it's an integer
#                 score = int(score)
#         except ValueError:
#             raise HTTPException(status_code=500, detail="Invalid prediction format")
        
#         # Return the prediction
#         return {"accessibility_score": score}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict-accessibility-score")
def predictAccessibility(features: VenueFeatures):
    score = random.randint(75, 90)  # Generates a random score between 75 and 90
    return {"accessibility_score": score}
    
@app.get("/weather-report")
def predictWeather():
    return {
        "Temperature": round(random.uniform(10, 35), 1),  # Temperature in °C (10°C - 35°C)
        "Humidity": random.randint(30, 90),  # Humidity in percentage (30% - 90%)
        "WindSpeed": round(random.uniform(5, 25), 1),  # Wind Speed in km/h (5km/h - 25km/h)
        "PrecipitationProbability": random.randint(0, 100)  # Probability of rain (0% - 100%)
    }


def safetyReport():
    levels = ["Low", "Moderate", "High"]
    probabilities = [0.4, 0.4, 0.2]  # Corresponding probabilities

    return {
        "Hostility": random.choices(levels, probabilities)[0]
    }

def generate_random_features() -> VenueFeatures:
    # Define possible values for string fields
    availability_options = ["Available", "Not Available", "Limited"]
    lighting_options = ["Good", "Medium", "Poor"]
    noise_options = ["Low", "Medium", "High"]
    
    return VenueFeatures(
        venue_name=f"Venue_{random.randint(1, 100)}",
        ramp_availability=random.choice(availability_options),
        elevator_availability=random.choice(availability_options),
        accessible_toilets=random.choice(availability_options),
        wifi_availability=random.choice(availability_options),
        parking_availability=random.choice(availability_options),
        signage=random.choice(availability_options),
        staff_assistance=random.choice(availability_options),
        door_width=random.randint(70, 120),  # Standard door widths in cm
        lighting=random.choice(lighting_options),
        noise_level=random.choice(noise_options)
    )

@app.get("/random-accessibility-features")
def get_random_features():
    features = generate_random_features()
    return features

def get_simplified_traffic_data(city_name: str, destination: str, future_date: str):
    """Simplified version of traffic data collection with fewer time points"""
    start_time = datetime.strptime(future_date, "%Y-%m-%d")
    data_collection = {}
    
    # Only get one main transport location instead of multiple
    airport_location = get_transport_locations(city_name, True)[:1]
    
    # Only check traffic for key hours (morning, afternoon, evening)
    key_hours = [9, 14, 18]  # Reduced from checking every hour
    
    for hour in key_hours:
        current_time = start_time + timedelta(hours=hour)
        unix_timestamp = int(time.mktime(current_time.timetuple()))
        
        if airport_location:
            traffic_results = gmaps.distance_matrix(
                origins=airport_location,
                destinations=[destination],
                departure_time=unix_timestamp,
                traffic_model="best_guess",
                mode="driving"
            )
            
            origin = airport_location[0]
            duration_text = traffic_results["rows"][0]["elements"][0].get("duration_in_traffic", {}).get("text", "N/A")
            duration_value = traffic_results["rows"][0]["elements"][0].get("duration_in_traffic", {}).get("value", None)
            
            if origin not in data_collection:
                data_collection[origin] = {"times": {}}
            
            data_collection[origin]["times"][current_time.strftime("%H:%M")] = {
                "travel_time_text": duration_text,
                "travel_time_seconds": duration_value
            }
    
    return {"traffic_data": data_collection}

@app.get("/generate-random-places", response_model=PlaceResponse)
async def generate_random_places(event_type: str = "party"):
    try:
        # Read the JSON file
        with open('place_data.json', 'r') as file:
            all_places = json.load(file)
        
        # Filter places that match the event type (case-insensitive)
        matching_places = [
            place for place in all_places.get('places', [])
            if event_type.lower() in [et.lower() for et in place.get('event_types', [])]
        ]
        
        # If no matching places found, use all places
        if not matching_places:
            matching_places = all_places.get('places', [])
        
        # Select 20 random unique places
        selected_places = random.sample(
            matching_places,
            min(20, len(matching_places))  # Ensure we don't try to sample more than available
        )
        
        return PlaceResponse(places=selected_places)
        
    except Exception as e:
        print(f"Error generating places: {str(e)}")
        return PlaceResponse(places=[{
            "name": "Error",
            "address": "Could not generate place recommendations at this time",
            "capacity": "Unknown",
            "features": ["Please try again later"],
            "website": "",
            "state": "Unknown",
            "estimated_cost": "Unknown",
            "event_types": [event_type]
        }])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)