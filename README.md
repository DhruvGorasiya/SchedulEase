# SchedulEase

AI Innovalte Hackathon Project. Team 14

- **Frontend:** User interface for event planning, venue browsing, and analytics.
- **Backend:** REST API for chat, venue search, scoring, and data aggregation.
- **AI/ML:** Powers recommendations, accessibility, and safety predictions.

---

## Tech Stack

- **Frontend:** Next.js, React, TailwindCSS, Mapbox, Clerk (auth)
- **Backend:** FastAPI, Python, Pydantic, Google Maps API, OpenAI API
- **ML/AI:** scikit-learn, YOLO (Ultralytics), LangChain, OpenAI GPT-4
- **Other:** Docker (optional), Jupyter (for model dev), Pandas, joblib

---

## Getting Started

### Backend Setup

1. **Install dependencies:**
   ```bash
   cd Backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   - Create a `.env` file in `Backend/` with:
     ```
     OPENAI_API_KEY=your_openai_key
     GOOGLE_API_KEY=your_google_maps_key
     ```

3. **Run the backend server:**
   ```bash
   uvicorn main:app --reload
   ```
   The API will be available at `http://localhost:8000`.

### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd SchedulEase
   npm install
   ```

2. **Run the frontend:**
   ```bash
   npm run dev
   ```
   The app will be available at [http://localhost:3000](http://localhost:3000).

---

## API Overview

- `POST /api/ai_message` — Conversational endpoint for event planning.
- `GET /traffic` — Get traffic data for a city/venue.
- `POST /predict-accessibility-score` — ML-based accessibility scoring.
- `GET /weather-report` — Real-time weather for venues.
- `GET /generate-random-places` — Generate sample venues.
- `POST /api/save-venue` — Save a venue to favorites.
- `GET /api/saved-venues` — Retrieve saved venues.

See `Backend/main.py` for full details.

---

## AI & ML Capabilities

- **Venue Recommendation:** Uses OpenAI GPT-4 to suggest real venues based on event type, location, budget, and attendees.
- **Accessibility Prediction:** ML model (scikit-learn) predicts venue accessibility from features (ramps, elevators, etc.).
- **Safety Analysis:** Combines crime prediction (scikit-learn), CCTV object detection (YOLO), and social media analysis (LangChain + OpenAI) for real-time safety scoring.
- **Weather & Traffic:** Integrates with external APIs for up-to-date forecasts.

---

## Contributing

1. Fork the repo and create your branch.
2. Commit your changes and open a PR.
3. For major changes, open an issue first to discuss.

---

## License

This project is for the AI Innovate Hackathon (Team 14). For other uses, please contact the authors.

---

## Authors

- Team 14, AI Innovate Hackathon
