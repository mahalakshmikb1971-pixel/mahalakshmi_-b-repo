"""
AI-Based Renewable and Sustainable Energy Management System
Main Flask Application
"""

import os
import json
import random
import math
from datetime import datetime, timedelta, date
from functools import wraps

from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash, jsonify)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# ── App Setup ──────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'energy-ai-secret-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///energy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ── Models ─────────────────────────────────────────────────────────────────────

class User(db.Model):
    __tablename__ = 'users'
    id              = db.Column(db.Integer, primary_key=True)
    username        = db.Column(db.String(80), unique=True, nullable=False)
    email           = db.Column(db.String(120), unique=True, nullable=False)
    password_hash   = db.Column(db.String(256), nullable=False)
    full_name       = db.Column(db.String(120))
    location        = db.Column(db.String(100), default='Chennai, India')
    solar_capacity  = db.Column(db.Float, default=5.0)
    grid_rate       = db.Column(db.Float, default=8.0)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

class WeatherRecord(db.Model):
    __tablename__ = 'weather_records'
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date        = db.Column(db.Date, nullable=False)
    hour        = db.Column(db.Integer, nullable=False)
    temperature = db.Column(db.Float)
    humidity    = db.Column(db.Float)
    cloud_cover = db.Column(db.Float)
    wind_speed  = db.Column(db.Float)
    condition   = db.Column(db.String(50))
    uv_index    = db.Column(db.Float)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

class SolarRecord(db.Model):
    __tablename__ = 'solar_records'
    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date          = db.Column(db.Date, nullable=False)
    hour          = db.Column(db.Integer, nullable=False)
    predicted_kwh = db.Column(db.Float, default=0.0)
    actual_kwh    = db.Column(db.Float, default=0.0)
    irradiance    = db.Column(db.Float, default=0.0)
    efficiency    = db.Column(db.Float, default=0.0)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

class Appliance(db.Model):
    __tablename__ = 'appliances'
    id               = db.Column(db.Integer, primary_key=True)
    user_id          = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name             = db.Column(db.String(100), nullable=False)
    power_watts      = db.Column(db.Float, nullable=False)
    category         = db.Column(db.String(50))
    priority         = db.Column(db.Integer, default=5)
    flexible_timing  = db.Column(db.Integer, default=1)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

class ApplianceUsage(db.Model):
    __tablename__ = 'appliance_usage'
    id               = db.Column(db.Integer, primary_key=True)
    user_id          = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    appliance_id     = db.Column(db.Integer, db.ForeignKey('appliances.id'), nullable=False)
    date             = db.Column(db.Date, nullable=False)
    start_hour       = db.Column(db.Integer, nullable=False)
    duration_hours   = db.Column(db.Float, nullable=False)
    energy_kwh       = db.Column(db.Float, nullable=False)
    source           = db.Column(db.String(10), default='grid')
    recommended_slot = db.Column(db.Integer, default=0)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

class EnergyDaily(db.Model):
    __tablename__ = 'energy_daily'
    id                    = db.Column(db.Integer, primary_key=True)
    user_id               = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date                  = db.Column(db.Date, nullable=False)
    solar_generated_kwh   = db.Column(db.Float, default=0.0)
    solar_used_kwh        = db.Column(db.Float, default=0.0)
    grid_used_kwh         = db.Column(db.Float, default=0.0)
    solar_exported_kwh    = db.Column(db.Float, default=0.0)
    total_consumption_kwh = db.Column(db.Float, default=0.0)
    peak_solar_hour       = db.Column(db.Integer)
    carbon_saved_kg       = db.Column(db.Float, default=0.0)
    bill_amount           = db.Column(db.Float, default=0.0)
    created_at            = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'date'),)

class EnergyHourly(db.Model):
    __tablename__ = 'energy_hourly'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date       = db.Column(db.Date, nullable=False)
    hour       = db.Column(db.Integer, nullable=False)
    solar_kwh  = db.Column(db.Float, default=0.0)
    grid_kwh   = db.Column(db.Float, default=0.0)
    total_kwh  = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Bill(db.Model):
    __tablename__ = 'bills'
    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    month         = db.Column(db.String(7), nullable=False)
    grid_units    = db.Column(db.Float, default=0.0)
    rate_per_unit = db.Column(db.Float, default=8.0)
    base_charge   = db.Column(db.Float, default=100.0)
    tax_amount    = db.Column(db.Float, default=0.0)
    total_amount  = db.Column(db.Float, default=0.0)
    solar_savings = db.Column(db.Float, default=0.0)
    generated_at  = db.Column(db.DateTime, default=datetime.utcnow)

class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    id                      = db.Column(db.Integer, primary_key=True)
    user_id                 = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date                    = db.Column(db.Date, nullable=False)
    appliance_id            = db.Column(db.Integer, db.ForeignKey('appliances.id'))
    recommended_start_hour  = db.Column(db.Integer)
    recommended_end_hour    = db.Column(db.Integer)
    reason                  = db.Column(db.Text)
    source                  = db.Column(db.String(10), default='solar')
    accepted                = db.Column(db.Integer, default=0)
    created_at              = db.Column(db.DateTime, default=datetime.utcnow)

# ── Auth Decorator ─────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def current_user():
    return User.query.get(session.get('user_id'))

# ── AI / Simulation Helpers ────────────────────────────────────────────────────

WEATHER_CONDITIONS = ['Sunny', 'Partly Cloudy', 'Cloudy', 'Overcast', 'Light Rain', 'Heavy Rain']
CONDITION_CLOUD = {'Sunny': 5, 'Partly Cloudy': 30, 'Cloudy': 65, 'Overcast': 85,
                   'Light Rain': 90, 'Heavy Rain': 98}

def predict_weather(location: str, days: int = 7):
    """Simulate AI weather prediction for the next `days` days."""
    forecast = []
    base_temp = 32 if 'Chennai' in location or 'India' in location else 22
    for d in range(days):
        day = date.today() + timedelta(days=d)
        condition = random.choice(WEATHER_CONDITIONS[:4] if d < 3 else WEATHER_CONDITIONS)
        cloud = CONDITION_CLOUD[condition] + random.uniform(-5, 5)
        cloud = max(0, min(100, cloud))
        forecast.append({
            'date': day.isoformat(),
            'condition': condition,
            'temperature': round(base_temp + random.uniform(-3, 5), 1),
            'humidity': round(random.uniform(55, 85), 1),
            'cloud_cover': round(cloud, 1),
            'wind_speed': round(random.uniform(5, 25), 1),
            'uv_index': round(max(0, 10 - cloud / 12), 1),
        })
    return forecast

def predict_solar_hourly(capacity_kwp: float, cloud_cover: float, date_obj):
    """
    Predict hourly solar generation using:
      - Gaussian irradiance curve (peak noon)
      - Cloud attenuation
      - Panel efficiency ~18 %
    Returns list of 24 hourly kWh values.
    """
    efficiency = 0.18
    panel_area = capacity_kwp / (1000 * efficiency) * 1000  # m²
    hourly = []
    for h in range(24):
        if h < 6 or h > 18:
            irr = 0.0
        else:
            # Gaussian centred at 12:00
            irr = 1000 * math.exp(-((h - 12) ** 2) / 18)
            # Cloud attenuation
            irr *= (1 - cloud_cover / 100 * 0.85)
            irr += random.uniform(-20, 20)
            irr = max(0, irr)
        kwh = round(irr * panel_area * efficiency / 1000, 3)
        hourly.append({'hour': h, 'irradiance': round(irr, 1), 'kwh': kwh})
    return hourly

def recommend_appliances(appliances, solar_hourly):
    """
    Simple AI rule engine:
      - Find hours where solar surplus > appliance power
      - Assign flexible appliances to solar-rich windows
    """
    recs = []
    solar_by_hour = {s['hour']: s['kwh'] for s in solar_hourly}
    # Sort appliances: low priority (high number) and flexible first
    flex = [a for a in appliances if a.flexible_timing]
    for appl in flex:
        appl_kw = appl.power_watts / 1000
        best_hour = None
        best_surplus = -1
        for h in range(6, 19):
            surplus = solar_by_hour.get(h, 0) - appl_kw
            if surplus > best_surplus:
                best_surplus = surplus
                best_hour = h
        if best_hour is not None:
            source = 'solar' if best_surplus > 0 else 'grid'
            reason = (f"Solar surplus of {round(best_surplus, 2)} kWh at {best_hour}:00"
                      if source == 'solar'
                      else f"No solar surplus; grid recommended at {best_hour}:00")
            recs.append({
                'appliance_id': appl.id,
                'appliance_name': appl.name,
                'power_watts': appl.power_watts,
                'recommended_start': best_hour,
                'recommended_end': best_hour + 2,
                'source': source,
                'reason': reason,
            })
    return recs

def generate_sample_history(user_id: int, days: int = 30):
    """Generate 30 days of realistic sample energy history."""
    user = User.query.get(user_id)
    for d in range(days, 0, -1):
        day = date.today() - timedelta(days=d)
        cloud = random.uniform(10, 70)
        solar_h = predict_solar_hourly(user.solar_capacity, cloud, day)
        solar_gen = sum(h['kwh'] for h in solar_h)
        consumption = round(random.uniform(8, 20), 2)
        solar_used = round(min(solar_gen * 0.85, consumption), 2)
        grid_used = round(max(0, consumption - solar_used), 2)
        exported = round(max(0, solar_gen - solar_used), 2)
        carbon = round(solar_used * 0.82, 2)   # 0.82 kg CO₂/kWh India grid
        bill = round(grid_used * user.grid_rate + 100, 2)

        # Upsert daily record
        rec = EnergyDaily.query.filter_by(user_id=user_id, date=day).first()
        if not rec:
            rec = EnergyDaily(user_id=user_id, date=day)
            db.session.add(rec)
        rec.solar_generated_kwh   = round(solar_gen, 2)
        rec.solar_used_kwh        = solar_used
        rec.grid_used_kwh         = grid_used
        rec.solar_exported_kwh    = exported
        rec.total_consumption_kwh = consumption
        rec.peak_solar_hour       = 12
        rec.carbon_saved_kg       = carbon
        rec.bill_amount           = bill

        # Hourly
        for h_data in solar_h:
            h = h_data['hour']
            s_kwh = h_data['kwh']
            g_kwh = round(random.uniform(0.1, 1.0), 3) if (h < 6 or h > 18) else round(random.uniform(0, 0.5), 3)
            ex = EnergyHourly(user_id=user_id, date=day, hour=h,
                              solar_kwh=s_kwh, grid_kwh=g_kwh,
                              total_kwh=round(s_kwh + g_kwh, 3))
            db.session.add(ex)

    db.session.commit()

# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# ── Auth ───────────────────────────────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f'Welcome back, {user.full_name or user.username}!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username      = request.form.get('username', '').strip()
        email         = request.form.get('email', '').strip()
        password      = request.form.get('password', '')
        full_name     = request.form.get('full_name', '').strip()
        location      = request.form.get('location', 'Chennai, India').strip()
        solar_capacity= float(request.form.get('solar_capacity', 5.0))

        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('register.html')

        user = User(
            username=username, email=email,
            password_hash=generate_password_hash(password),
            full_name=full_name, location=location,
            solar_capacity=solar_capacity
        )
        db.session.add(user)
        db.session.commit()

        # Seed default appliances
        defaults = [
            ('Air Conditioner', 1500, 'HVAC', 3, 1),
            ('Washing Machine', 800, 'Laundry', 5, 1),
            ('Water Heater', 2000, 'Water', 4, 1),
            ('EV Charger', 3300, 'EV', 6, 1),
            ('Refrigerator', 150, 'Kitchen', 1, 0),
            ('Dishwasher', 1200, 'Kitchen', 7, 1),
            ('Lighting', 200, 'Lighting', 2, 0),
        ]
        for name, watts, cat, prio, flex in defaults:
            db.session.add(Appliance(user_id=user.id, name=name,
                                     power_watts=watts, category=cat,
                                     priority=prio, flexible_timing=flex))
        db.session.commit()

        # Generate history data
        generate_sample_history(user.id, 30)

        session['user_id'] = user.id
        session['username'] = user.username
        flash('Registration successful! Welcome aboard.', 'success')
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# ── Dashboard ──────────────────────────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    user = current_user()
    today = date.today()

    # Today's energy summary
    today_rec = EnergyDaily.query.filter_by(user_id=user.id, date=today).first()
    if not today_rec:
        # Generate today live
        cloud = random.uniform(10, 40)
        solar_h = predict_solar_hourly(user.solar_capacity, cloud, today)
        solar_gen = sum(h['kwh'] for h in solar_h)
        consumption = round(random.uniform(8, 15), 2)
        solar_used = round(min(solar_gen * 0.85, consumption), 2)
        grid_used = round(max(0, consumption - solar_used), 2)
        today_rec = EnergyDaily(
            user_id=user.id, date=today,
            solar_generated_kwh=round(solar_gen, 2),
            solar_used_kwh=solar_used, grid_used_kwh=grid_used,
            solar_exported_kwh=round(max(0, solar_gen - solar_used), 2),
            total_consumption_kwh=consumption,
            carbon_saved_kg=round(solar_used * 0.82, 2),
            bill_amount=round(grid_used * user.grid_rate + 100, 2),
        )
        db.session.add(today_rec)
        db.session.commit()

    # Last 7 days for charts
    week_data = (EnergyDaily.query
                 .filter_by(user_id=user.id)
                 .filter(EnergyDaily.date >= today - timedelta(days=6))
                 .order_by(EnergyDaily.date)
                 .all())

    chart_labels = [r.date.strftime('%d %b') for r in week_data]
    chart_solar  = [r.solar_generated_kwh for r in week_data]
    chart_grid   = [r.grid_used_kwh for r in week_data]
    chart_carbon = [r.carbon_saved_kg for r in week_data]

    # Monthly totals
    month_start = today.replace(day=1)
    monthly = (EnergyDaily.query
               .filter_by(user_id=user.id)
               .filter(EnergyDaily.date >= month_start)
               .all())
    monthly_solar  = sum(r.solar_generated_kwh for r in monthly)
    monthly_grid   = sum(r.grid_used_kwh for r in monthly)
    monthly_carbon = sum(r.carbon_saved_kg for r in monthly)
    monthly_saving = round(monthly_solar * user.grid_rate, 2)

    # Hourly for today (live-ish)
    hourly_data = (EnergyHourly.query
                   .filter_by(user_id=user.id, date=today)
                   .order_by(EnergyHourly.hour)
                   .all())
    hourly_labels = [f'{h.hour:02d}:00' for h in hourly_data]
    hourly_solar  = [h.solar_kwh for h in hourly_data]
    hourly_grid   = [h.grid_kwh for h in hourly_data]

    return render_template('dashboard.html',
        user=user, today=today_rec,
        chart_labels=json.dumps(chart_labels),
        chart_solar=json.dumps(chart_solar),
        chart_grid=json.dumps(chart_grid),
        chart_carbon=json.dumps(chart_carbon),
        monthly_solar=round(monthly_solar, 2),
        monthly_grid=round(monthly_grid, 2),
        monthly_carbon=round(monthly_carbon, 2),
        monthly_saving=monthly_saving,
        hourly_labels=json.dumps(hourly_labels),
        hourly_solar=json.dumps(hourly_solar),
        hourly_grid=json.dumps(hourly_grid),
    )

# ── Weather Prediction ─────────────────────────────────────────────────────────

@app.route('/weather')
@login_required
def weather():
    user = current_user()
    forecast = predict_weather(user.location, days=7)
    return render_template('weather.html', user=user, forecast=forecast)

@app.route('/api/weather')
@login_required
def api_weather():
    user = current_user()
    return jsonify(predict_weather(user.location, days=7))

# ── Solar Prediction ───────────────────────────────────────────────────────────

@app.route('/solar')
@login_required
def solar():
    user = current_user()
    forecast = predict_weather(user.location, days=7)
    # Build daily solar predictions
    solar_forecast = []
    for day in forecast:
        hourly = predict_solar_hourly(user.solar_capacity, day['cloud_cover'],
                                      date.fromisoformat(day['date']))
        daily_kwh = round(sum(h['kwh'] for h in hourly), 2)
        peak_irr  = max(h['irradiance'] for h in hourly)
        solar_forecast.append({
            **day,
            'daily_kwh': daily_kwh,
            'peak_irradiance': round(peak_irr, 1),
            'hourly': hourly,
        })
    # Today hourly for chart
    today_hourly = solar_forecast[0]['hourly']
    hour_labels  = [f"{h['hour']:02d}:00" for h in today_hourly]
    hour_kwh     = [h['kwh'] for h in today_hourly]
    return render_template('solar.html', user=user,
                           solar_forecast=solar_forecast,
                           hour_labels=json.dumps(hour_labels),
                           hour_kwh=json.dumps(hour_kwh))

# ── Appliance Recommendation ───────────────────────────────────────────────────

@app.route('/appliances', methods=['GET', 'POST'])
@login_required
def appliances():
    user = current_user()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            db.session.add(Appliance(
                user_id=user.id,
                name=request.form['name'],
                power_watts=float(request.form['power_watts']),
                category=request.form.get('category', 'Other'),
                priority=int(request.form.get('priority', 5)),
                flexible_timing=int(request.form.get('flexible_timing', 1)),
            ))
            db.session.commit()
            flash('Appliance added.', 'success')
        elif action == 'delete':
            Appliance.query.filter_by(id=int(request.form['appliance_id']),
                                      user_id=user.id).delete()
            db.session.commit()
            flash('Appliance removed.', 'info')
        return redirect(url_for('appliances'))

    user_appliances = Appliance.query.filter_by(user_id=user.id).all()
    # Get today forecast for recommendations
    weather_today = predict_weather(user.location, days=1)[0]
    solar_hourly  = predict_solar_hourly(user.solar_capacity,
                                         weather_today['cloud_cover'], date.today())
    recs = recommend_appliances(user_appliances, solar_hourly)

    # Save recommendations to DB
    for r in recs:
        rec = Recommendation(
            user_id=user.id,
            date=date.today(),
            appliance_id=r['appliance_id'],
            recommended_start_hour=r['recommended_start'],
            recommended_end_hour=r['recommended_end'],
            reason=r['reason'],
            source=r['source'],
        )
        db.session.add(rec)
    db.session.commit()

    return render_template('appliances.html', user=user,
                           appliances=user_appliances, recs=recs,
                           weather=weather_today)

# ── Energy Monitoring ──────────────────────────────────────────────────────────

@app.route('/monitoring')
@login_required
def monitoring():
    user = current_user()
    today = date.today()

    # 30-day data
    history = (EnergyDaily.query
               .filter_by(user_id=user.id)
               .filter(EnergyDaily.date >= today - timedelta(days=29))
               .order_by(EnergyDaily.date)
               .all())

    labels      = [r.date.strftime('%d %b') for r in history]
    solar_data  = [r.solar_generated_kwh for r in history]
    grid_data   = [r.grid_used_kwh for r in history]
    carbon_data = [r.carbon_saved_kg for r in history]

    total_solar  = round(sum(solar_data), 2)
    total_grid   = round(sum(grid_data), 2)
    total_carbon = round(sum(carbon_data), 2)
    solar_pct    = round(total_solar / (total_solar + total_grid) * 100, 1) if (total_solar + total_grid) else 0

    return render_template('monitoring.html', user=user,
                           history=history,
                           labels=json.dumps(labels),
                           solar_data=json.dumps(solar_data),
                           grid_data=json.dumps(grid_data),
                           carbon_data=json.dumps(carbon_data),
                           total_solar=total_solar, total_grid=total_grid,
                           total_carbon=total_carbon, solar_pct=solar_pct)

# ── Bill Calculator ────────────────────────────────────────────────────────────

@app.route('/bill', methods=['GET', 'POST'])
@login_required
def bill():
    user = current_user()
    today = date.today()
    result = None

    if request.method == 'POST':
        month       = request.form.get('month', today.strftime('%Y-%m'))
        rate        = float(request.form.get('rate', user.grid_rate))
        base_charge = float(request.form.get('base_charge', 100))

        # Sum grid usage for selected month
        month_start = date(int(month[:4]), int(month[5:7]), 1)
        next_m = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
        records = (EnergyDaily.query
                   .filter_by(user_id=user.id)
                   .filter(EnergyDaily.date >= month_start, EnergyDaily.date < next_m)
                   .all())
        grid_units   = round(sum(r.grid_used_kwh for r in records), 2)
        solar_saved  = round(sum(r.solar_used_kwh for r in records), 2)
        energy_cost  = round(grid_units * rate, 2)
        tax          = round(energy_cost * 0.05, 2)
        total        = round(energy_cost + base_charge + tax, 2)
        without_solar= round((grid_units + solar_saved) * rate + base_charge, 2)
        saved        = round(without_solar - total, 2)
        carbon_saved = round(solar_saved * 0.82, 2)

        result = dict(month=month, grid_units=grid_units, rate=rate,
                      energy_cost=energy_cost, base_charge=base_charge,
                      tax=tax, total=total, solar_saved=solar_saved,
                      without_solar=without_solar, saved=saved,
                      carbon_saved=carbon_saved)

        # Save bill
        b = Bill(user_id=user.id, month=month, grid_units=grid_units,
                 rate_per_unit=rate, base_charge=base_charge,
                 tax_amount=tax, total_amount=total, solar_savings=saved)
        db.session.add(b)
        db.session.commit()

    past_bills = (Bill.query.filter_by(user_id=user.id)
                  .order_by(Bill.generated_at.desc()).limit(6).all())
    return render_template('bill.html', user=user, result=result,
                           past_bills=past_bills,
                           current_month=today.strftime('%Y-%m'))

# ── Reports ────────────────────────────────────────────────────────────────────

@app.route('/reports')
@login_required
def reports():
    user = current_user()
    today = date.today()

    # 12-month monthly aggregates
    monthly_agg = []
    for m in range(11, -1, -1):
        ref = today - timedelta(days=m * 30)
        m_start = ref.replace(day=1)
        m_end   = (m_start + timedelta(days=32)).replace(day=1)
        recs = (EnergyDaily.query
                .filter_by(user_id=user.id)
                .filter(EnergyDaily.date >= m_start, EnergyDaily.date < m_end)
                .all())
        monthly_agg.append({
            'month': m_start.strftime('%b %Y'),
            'solar': round(sum(r.solar_generated_kwh for r in recs), 2),
            'grid':  round(sum(r.grid_used_kwh for r in recs), 2),
            'carbon':round(sum(r.carbon_saved_kg for r in recs), 2),
            'bill':  round(sum(r.bill_amount for r in recs), 2),
        })

    m_labels = json.dumps([m['month'] for m in monthly_agg])
    m_solar  = json.dumps([m['solar']  for m in monthly_agg])
    m_grid   = json.dumps([m['grid']   for m in monthly_agg])
    m_carbon = json.dumps([m['carbon'] for m in monthly_agg])
    m_bill   = json.dumps([m['bill']   for m in monthly_agg])

    # Totals
    all_records = EnergyDaily.query.filter_by(user_id=user.id).all()
    total_solar  = round(sum(r.solar_generated_kwh for r in all_records), 2)
    total_grid   = round(sum(r.grid_used_kwh for r in all_records), 2)
    total_carbon = round(sum(r.carbon_saved_kg for r in all_records), 2)
    total_saving = round(total_solar * user.grid_rate, 2)
    trees_equiv  = round(total_carbon / 21.7, 1)   # avg tree absorbs 21.7 kg/year

    return render_template('reports.html', user=user,
                           monthly_agg=monthly_agg,
                           m_labels=m_labels, m_solar=m_solar,
                           m_grid=m_grid, m_carbon=m_carbon, m_bill=m_bill,
                           total_solar=total_solar, total_grid=total_grid,
                           total_carbon=total_carbon, total_saving=total_saving,
                           trees_equiv=trees_equiv)

# ── Settings ───────────────────────────────────────────────────────────────────

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    user = current_user()
    if request.method == 'POST':
        user.full_name      = request.form.get('full_name', user.full_name)
        user.location       = request.form.get('location', user.location)
        user.solar_capacity = float(request.form.get('solar_capacity', user.solar_capacity))
        user.grid_rate      = float(request.form.get('grid_rate', user.grid_rate))
        new_pw = request.form.get('new_password', '').strip()
        if new_pw:
            user.password_hash = generate_password_hash(new_pw)
        db.session.commit()
        flash('Settings saved.', 'success')
        return redirect(url_for('settings'))
    return render_template('settings.html', user=user)

# ── API Endpoints ──────────────────────────────────────────────────────────────

@app.route('/api/dashboard_summary')
@login_required
def api_dashboard():
    user = current_user()
    today_rec = EnergyDaily.query.filter_by(user_id=user.id,
                                            date=date.today()).first()
    if not today_rec:
        return jsonify({'error': 'No data for today'})
    return jsonify({
        'solar_generated': today_rec.solar_generated_kwh,
        'solar_used':      today_rec.solar_used_kwh,
        'grid_used':       today_rec.grid_used_kwh,
        'carbon_saved':    today_rec.carbon_saved_kg,
        'bill_estimate':   today_rec.bill_amount,
    })

@app.route('/api/solar_forecast')
@login_required
def api_solar_forecast():
    user = current_user()
    cloud = float(request.args.get('cloud', 20))
    hourly = predict_solar_hourly(user.solar_capacity, cloud, date.today())
    return jsonify(hourly)

# ── Init ───────────────────────────────────────────────────────────────────────

def create_demo_user():
    """Create demo user if not exists."""
    if not User.query.filter_by(username='demo').first():
        u = User(username='demo', email='demo@energyai.com',
                 password_hash=generate_password_hash('demo123'),
                 full_name='Demo User', location='Chennai, India',
                 solar_capacity=5.0, grid_rate=8.0)
        db.session.add(u)
        db.session.commit()
        for name, watts, cat, prio, flex in [
            ('Air Conditioner', 1500, 'HVAC', 3, 1),
            ('Washing Machine', 800, 'Laundry', 5, 1),
            ('Water Heater', 2000, 'Water', 4, 1),
            ('EV Charger', 3300, 'EV', 6, 1),
            ('Refrigerator', 150, 'Kitchen', 1, 0),
            ('Dishwasher', 1200, 'Kitchen', 7, 1),
            ('Lighting', 200, 'Lighting', 2, 0),
        ]:
            db.session.add(Appliance(user_id=u.id, name=name,
                                     power_watts=watts, category=cat,
                                     priority=prio, flexible_timing=flex))
        db.session.commit()
        generate_sample_history(u.id, 30)

with app.app_context():
    db.create_all()
    create_demo_user()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
