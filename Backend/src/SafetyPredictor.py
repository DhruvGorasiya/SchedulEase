from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, AgentType
import datetime
import joblib
import pandas as pd
import numpy as np
import cv2
from ultralytics import YOLO
import os

# Set up OpenAI API key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")  # Replace with actual API key

# Initialize LLM
llm = ChatOpenAI(model_name="gpt-4", temperature=0.5)

# Define memory for conversation history
memory = ConversationBufferMemory(memory_key="chat_history")

# Load the trained model
MODEL_FILENAME = "C:\SchedulEase\Backend\src\model.pkl"
crime_model = joblib.load(MODEL_FILENAME)

# Mapping for day of the week
days_mapping = {
    'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
    'Friday': 4, 'Saturday': 5, 'Sunday': 6
}

# Cyclical Encoding for Time Features
def add_cyclical_features(df):
    df['HOUR_SIN'] = np.sin(2 * np.pi * df['HOUR'] / 24)
    df['HOUR_COS'] = np.cos(2 * np.pi * df['HOUR'] / 24)
    df['MONTH_SIN'] = np.sin(2 * np.pi * (df['MONTH'] - 1) / 12)
    df['MONTH_COS'] = np.cos(2 * np.pi * (df['MONTH'] - 1) / 12)
    df['DAY_SIN'] = np.sin(2 * np.pi * df['DAY_OF_WEEK'] / 7)
    df['DAY_COS'] = np.cos(2 * np.pi * df['DAY_OF_WEEK'] / 7)
    return df.drop(['HOUR', 'MONTH', 'DAY_OF_WEEK'], axis=1)

# Predict Crime Function
def predict_crime(lat, long, hour, month, day_of_week):
    if isinstance(day_of_week, str):
        day_of_week = days_mapping[day_of_week.strip()]

    input_df = pd.DataFrame([{
        'Lat': lat,
        'Long': long,
        'HOUR': hour,
        'MONTH': month,
        'DAY_OF_WEEK': day_of_week
    }])

    input_processed = add_cyclical_features(input_df)
    return crime_model.predict(input_processed)[0]

# Load YOLO model for CCTV analysis
cctv_model = YOLO("yolov8n.pt")

# Function to analyze CCTV footage
def detect_suspicious_activity():
    cap = cv2.VideoCapture(0)  # Replace with actual CCTV stream
    ret, frame = cap.read()

    if not ret:
        return "No video feed available"

    results = cctv_model(frame)
    detected_objects = [cctv_model.names[int(box.cls[0])] for r in results for box in r.boxes]

    cap.release()
    return detected_objects

# Function to fetch AI-generated suspicious objects
def get_suspicious_objects():
    prompt = "List the objects or items that are considered suspicious or dangerous in a security surveillance setting."
    return llm.predict(prompt).lower().split(", ")

# Function to analyze social media alerts
def analyze_social_media(tweetts: str = None):
    if not tweetts:
        tweetts = ["Great Event. No issues."]
    threats = []
    print(tweetts, "tweets")
    for tweet in tweetts:
        response = llm.predict(f"Analyze the following tweet for security risks: {tweet}")

        if "threat" in response.lower():
            threats.append(response)

    print(threats)
    return threats if threats else "All clear"

# Crime Risk Summarization with AI-generated suspicious objects
def summarize_crime_risk(social_media_alert, cctv_output, lat, long, datetime_obj):
    suspicious_objects = get_suspicious_objects()

    # Extract time-related features
    hour = datetime_obj.hour
    month = datetime_obj.month
    day_of_week = datetime_obj.strftime("%A")

    # Ensure social_media_alert is a string
    if isinstance(social_media_alert, list):
        social_media_alert = ", ".join(social_media_alert)

    # Check for threats in social media alerts
    social_media_threat_detected = "threat" in social_media_alert.lower()

    # Check for suspicious objects in CCTV monitoring
    cctv_threat_detected = any(obj.lower() in suspicious_objects for obj in cctv_output)

    # Determine if a crime is likely
    if social_media_threat_detected or cctv_threat_detected:
        predicted_crime = predict_crime(lat, long, hour, month, day_of_week)
        return f"🚨 Alert: Suspicious activity detected! Possible crime or event at the Location: {predicted_crime}."



    return "✅ No crime detected or possible at the location at the given time."

# LangChain Tools for integration
def setup_security_agent():
    cctv_monitoring_tool = Tool(
        name="CCTV Monitoring",
        func=detect_suspicious_activity,
        description="Analyzes CCTV footage for suspicious activities."
    )

    social_media_tool = Tool(
        name="Social Media Monitoring",
        func=analyze_social_media,
        description="Analyzes social media posts for potential security threats."
    )

    # Initialize AI Security Agent
    security_agent = initialize_agent(
        tools=[cctv_monitoring_tool, social_media_tool],
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        memory=memory
    )
    return security_agent

# Main function to run the full security workflow
def run_security_workflow(lat, long, datetime_obj, tweets):
    social_media_alert = analyze_social_media(tweets)
    cctv_output = detect_suspicious_activity()
    summary = summarize_crime_risk(social_media_alert, cctv_output, lat, long, datetime_obj)
    return summary

# Example usage
if __name__ == "__main__":
    lat, long = 42.271661, -71.099534
    tweets = ["Safe"]
    datetime_obj = datetime.datetime(2025, 2, 15, 22, 0)  # Example timestamp
    summary = run_security_workflow(lat, long, datetime_obj, tweets)
    print(summary)