# ⚡ AI-Based Renewable & Sustainable Energy Management System

A full-stack web application that uses AI to predict solar energy availability, recommend optimal appliance usage schedules, monitor energy consumption, and calculate electricity bills — all in a modern, responsive dashboard.

---

## 🚀 Features

| Feature | Description |
|---|---|
| 🤖 **AI Weather Prediction** | 7-day forecast using AI simulation |
| ☀ **Solar Energy Forecast** | Hourly & daily solar generation prediction |
| ⊞ **Appliance Scheduler** | AI recommends best time slots using solar surplus |
| ⚡ **Grid Auto-Switch** | Switches to grid when solar is insufficient |
| 📊 **Energy Monitoring** | Separate tracking of solar vs grid usage |
| ₹ **Bill Calculator** | Grid bill calculation with solar savings report |
| 🌿 **Carbon Tracker** | CO₂ offset and tree-equivalent display |
| 📋 **Reports** | 12-month analytics and charts |
| 🔒 **Auth** | Login & registration with hashed passwords |

---

## 📁 Project Structure

```
energy_mgmt/
├── app.py                     # Main Flask application
├── requirements.txt           # Python dependencies
├── README.md
├── database/
│   └── schema.sql             # Database schema + sample data
├── instance/
│   └── energy.db              # SQLite database (auto-created)
├── static/
│   ├── css/
│   │   └── style.css          # Complete UI stylesheet
│   └── js/
│       └── main.js            # Frontend JavaScript
└── templates/
    ├── base.html              # Sidebar layout
    ├── login.html             # Login page
    ├── register.html          # Registration page
    ├── dashboard.html         # Main dashboard
    ├── weather.html           # Weather AI page
    ├── solar.html             # Solar forecast page
    ├── appliances.html        # Appliance recommendations
    ├── monitoring.html        # Energy monitoring
    ├── bill.html              # Bill calculator
    ├── reports.html           # Reports & analytics
    └── settings.html         # User settings
```

---

## 🛠 Setup Instructions

### Prerequisites
- Python 3.9+
- pip

### 1. Clone / Extract the project
```bash
cd energy_mgmt
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
python app.py
```

### 5. Open in browser
```
http://localhost:5000
```

---

## 🔑 Demo Login

| Field | Value |
|---|---|
| Username | `demo` |
| Password | `demo123` |

The demo account includes **30 days of sample energy data** pre-loaded automatically.

---

## 🧠 AI System Details

### Weather Prediction
- Simulates AI forecast using randomised realistic weather patterns
- Location-aware base temperature (Chennai defaults to ~32°C)
- 7-day rolling prediction with UV index, cloud cover, humidity, wind

### Solar Generation Model
- **Gaussian Irradiance Curve**: Peak solar at noon, tapering off toward morning/evening
- **Cloud Attenuation Factor**: `irradiance × (1 - cloud_cover × 0.85)`
- **Panel Efficiency**: 18% (industry standard mono-crystalline)
- Output in kWh per hour for each day

### Appliance Scheduler
- Finds the hour with maximum solar surplus for each flexible appliance
- Assigns solar-powered slot if surplus > appliance power; else grid slot
- Stores recommendations in database with accept/reject tracking

### Grid Auto-Switch Logic
```
if solar_generated >= home_load:
    source = "solar"
    export_excess_to_grid()
else:
    source = "solar + grid"
    grid_fills_the_gap()
```

### Carbon Calculation
- India grid carbon factor: **0.82 kg CO₂/kWh**
- Tree equivalent: **21.7 kg CO₂ absorbed per tree per year**

---

## 🗃 Database Schema

| Table | Purpose |
|---|---|
| `users` | Login, profile, solar capacity, grid rate |
| `weather_records` | Hourly weather data |
| `solar_records` | Hourly solar predictions + actuals |
| `appliances` | User's appliance list |
| `appliance_usage` | Appliance usage logs (solar/grid) |
| `energy_daily` | Daily energy summary |
| `energy_hourly` | Hourly energy breakdown |
| `bills` | Calculated bill records |
| `recommendations` | AI appliance schedule suggestions |

---

## 🎨 Tech Stack

- **Backend**: Python 3, Flask, Flask-SQLAlchemy
- **Database**: SQLite (upgradeable to MySQL/PostgreSQL)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Charts**: Chart.js 4.4
- **Fonts**: Google Fonts (Inter + Space Grotesk)
- **Auth**: Werkzeug PBKDF2 password hashing

---

## 📦 Upgrading to MySQL

Replace the SQLAlchemy URI in `app.py`:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'mysql+pymysql://user:password@localhost/energy_db'
```
Then install: `pip install PyMySQL`

---

## 📝 License
MIT — Free to use for academic and educational purposes.
