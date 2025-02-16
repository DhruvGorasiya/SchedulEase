import pandas as pd

def preprocess_data(filepath):
    # Load data
    data = pd.read_csv(filepath)
    
    # Preprocess data (e.g., encode categorical variables)
    data["ramp_availability"] = data["ramp_availability"].map({"Yes": 1, "No": 0})
    data["elevator_availability"] = data["elevator_availability"].map({"Yes": 1, "No": 0})
    data["accessible_toilets"] = data["accessible_toilets"].map({"Yes": 1, "No": 0})
    data["wifi_availability"] = data["wifi_availability"].map({"Yes": 1, "No": 0})
    data["parking_availability"] = data["parking_availability"].map({"Yes": 1, "No": 0})
    data["signage"] = data["signage"].map({"Good": 2, "Fair": 1, "Poor": 0})
    data["staff_assistance"] = data["staff_assistance"].map({"Yes": 1, "No": 0})
    data["lighting"] = data["lighting"].map({"Good": 2, "Fair": 1, "Poor": 0})
    data["noise_level"] = data["noise_level"].map({"Low": 2, "Medium": 1, "High": 0})
    
    return data