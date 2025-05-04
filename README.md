# 🌠 Sky Session Planner

A passion-project **Flask** web application that helps amateur astronomers choose the location with the best stargazing—conditions anywhere on Earth. It utilizes several APIs to fetch precise geographic data, local weather forecasts, and celestial-event calculations for a given locations. Click anywhere on the map (or search by city name) to get:
- **Geographical** info: terrain type, elevation, nearest urban centers  
- **Weather** forecast: current conditions, hourly/daily charts (temperature, cloud cover, precipitation)  
- **Astronomical** events: moonrise/set, visible planets, conjunctions, meteor showers

Plan your next sky-watching sesion with confidence!

---

## Features

- **Interactive map** (Leaflet) with click-to-select coordinates; global coverage!  
- **Elevation** from OpenElevation API  
- **Weather** from Open-Meteo API, displayed as dynamic charts (Chart.js)  
- **Astronomical** calculations via Skyfield (moon, visible planets, conjunctions)  
- **Meteor shower** calendar with Zenithal Hourly Rate (ZHR)  
- **Responsive sidebar** with tabs for different data categories
- **City lookup** (OpenStreetMap Nominatim)  

---

## Installation

1. **Clone the repo**  
   ```bash
   git clone https://github.com/your-username/star-session-planner.git
   cd star-session-planner
   ```

2. **Create & activate a virtualenv**  
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**  
   ```bash
   export FLASK_APP=app
   flask run
   ```
   Then open [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## Project Structure

```
star-session-planner/
├── app/
│   ├── clients/       # API wrappers (OpenMeteo, OpenElevation, OSM, Nominatim)
│   ├── services/      # Distance calculator, astronomical events
│   ├── templates/     # Jinja2 HTML templates
│   ├── static/        # CSS, JS (Leaflet, Chart.js, jQuery)
│   ├── forms.py       # WTForms city search
│   ├── models.py      # SQLAlchemy (for future expansions)
│   └── routes.py      # Flask routes & business logic
├── requirements.txt
└── README.md
```

---

## Usage

1. **Click on the map**, or **search by city** in the top-left form.  
2. Wait for the **loading indicator**, then browse through the **Geographical**, **Weather**, and **Astronomical** tabs.  
3. Resize the sidebar by dragging its left edge to customize chart layouts.  

---

## Dependencies

```text
Flask==1.1.2
flask_sqlalchemy==3.1.1
flask_wtf==1.2.2
geopy==2.4.1
numpy==1.24.3
openmeteo_requests==1.4.0
pandas==1.4.4
pytz==2023.3.post1
Requests==2.32.3
requests_cache==1.2.1
retry_requests==2.0.0
scipy==1.9.3
skyfield==1.53
timezonefinder==6.5.9
WTForms==3.2.1
```
