import os
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

def train_model(data):
    # Define the prompt template
    prompt_template = """
    Given the following features of a venue, predict the accessibility score:

    Venue Name: {venue_name}
    Ramp Availability: {ramp_availability}
    Elevator Availability: {elevator_availability}
    Accessible Toilets: {accessible_toilets}
    Wi-Fi Availability: {wifi_availability}
    Parking Availability: {parking_availability}
    Signage: {signage}
    Staff Assistance: {staff_assistance}
    Door Width: {door_width} inches
    Lighting: {lighting}
    Noise Level: {noise_level}

    Predict the accessibility score (0-100):
    """

    prompt = PromptTemplate(
        input_variables=[
            "venue_name", "ramp_availability", "elevator_availability", "accessible_toilets",
            "wifi_availability", "parking_availability", "signage", "staff_assistance",
            "door_width", "lighting", "noise_level"
        ],
        template=prompt_template
    )

    # Initialize the LLM with your OpenAI API key
    llm = OpenAI(temperature=0, openai_api_key=os.getenv('OPENAI_API_KEY'))

    # Create the LLMChain
    model = LLMChain(llm=llm, prompt=prompt)
    
    return model