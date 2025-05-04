# 🌠 Sky Session Planner

A passion-project **Flask** web application that helps amateur astronomers choose the location with the best stargazing—conditions anywhere on Earth. It utilizes several APIs to fetch precise geographic data, local weather forecasts, and celestial-event calculations for a given locations. It presents all the information to the user and lets them compare different places by choosing them from an interactive map of typing a city name. Plan your next sky-watching sesion with confidence!

---

## 🔧 Features

- **Global Coverage**  
  Plan sessions for any latitude/longitude worldwide.  
- **Accurate Site Data**  
  • Pulls map coordinates & elevation via OpenStreetMap (Nominatim) & OpenElevation APIs  
- **Weather Integration**  
  • Fetches hourly forecasts from Open-Meteo to pinpoint clear-sky windows  
- **Celestial Calculations**  
  • Uses Skyfield to compute rise/set times, moon phase, and visible events  
- **Interactive UI**  
  • Dynamic calendars and map overlays built with vanilla JavaScript, HTML5, and CSS3  

---

## ⚙️ Tech Stack

| Layer                | Technologies                                              |
|----------------------|-----------------------------------------------------------|
| **Backend**          | Python 3 · Flask · Jinja2                                 |
| **Frontend**         | JavaScript (ES6+) · HTML5 · CSS3                          |
| **APIs & Data**      | OpenStreetMap (Nominatim) · OpenElevation · Open-Meteo    |
| **Astronomy**        | Skyfield                                                   |
| **Dev & Ops**        | Git · Docker · virtualenv                                 |

---

## 🚀 Quick Start

1. **Clone the repo**  
   ```bash
   git clone https://github.com/kjanus03/star-session-planner.git
   cd star-session-planner
