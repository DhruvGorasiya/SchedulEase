from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
import json
import re
import os
from openai import OpenAI

app = FastAPI()

# Initialize OpenAI client at the top level
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Clear conversations periodically (optional)
@app.on_event("startup")
async def startup_event():
    conversations.clear()

# Add CORS middleware
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
    predictionData: Optional[List[dict]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# Store conversation states
conversations: Dict[str, ConversationState] = {}

def generate_venue_recommendations(data: dict) -> List[dict]:
    # Remove client initialization from here since we're using the global client
    
    # Construct a more detailed prompt for realistic venues
    prompt = f"""As an expert event planner, recommend 20 real and currently operating venues in {data['location']} that would be perfect for a {data['event_type']} with {data['attendees']} attendees and a budget of {data['budget']}.

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
                "date": "{data['date']}",
                "budget": "{data['budget']}",
                "attendees": "{data['attendees']}"
            }}
        ]
        "predictionData": [
            {{
                "name": "Real Venue Name",
                "address": "Actual Street Address",
                "capacity": "Specific capacity range",
                "features": ["Real Feature 1", "Real Feature 2", "Real Feature 3"],
                "source": "Actual website URL",
                "date": "Actual date",
                "time": "Actual time",
                "budget": "Actual budget",
                "attendees": "Actual attendees",
                "state": "Actual state"
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
        
        # Add error handling for the response content
        if not response.choices or not response.choices[0].message.content:
            raise Exception("No response received from OpenAI")
            
        venues_data = json.loads(response.choices[0].message.content)
        return venues_data.get('venues', [])
    except Exception as e:
        print(f"Error generating venues: {str(e)}")
        return [{
            "name": "Error",
            "address": "Could not generate venue recommendations at this time",
            "capacity": "Unknown",
            "features": ["Please try again later"],
            "source": ""
        }]

def validate_input(question_type: str, user_input: str) -> tuple[bool, str]:
    """Validate user input and return (is_valid, processed_input)"""
    user_input = user_input.strip()
    
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
            if not re.match(r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}', user_input):
                return False, "I need a valid date format (DD/MM/YYYY or MM/DD/YYYY). "
            return True, user_input
        except:
            return False, "Please provide a valid date. "
    elif question_type == "time":
        if not re.match(r'\d{1,2}[:]\d{2}|^\d{1,2}\s*(?:am|pm|AM|PM)', user_input):
            return False, "I need a valid time format (e.g., 14:30 or 2:30 PM). "
        return True, user_input
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)