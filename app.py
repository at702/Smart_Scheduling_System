from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
import random
import sqlite3
from contextlib import closing

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Needed for flash messages

# Database configuration
DATABASE = 'clinic.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row  # Allows dictionary-style access to columns
    return db

def init_db():
    with closing(sqlite3.connect(DATABASE)) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

# Sample function to calculate wait times based on real data
def calculate_wait_times():
    db = get_db()
    
    # Get current appointments for each doctor
    doctors = db.execute("SELECT doctor_id, name FROM doctors").fetchall()
    
    wait_times = {}
    
    for doctor in doctors:
        # Count pending appointments (checked in but not seen)
        pending = db.execute("""
            SELECT COUNT(*) as count 
            FROM appointments 
            WHERE doctor_id = ? 
            AND check_in_time IS NOT NULL 
            AND seen_time IS NULL
        """, (doctor['doctor_id'],)).fetchone()['count']
        
        # Calculate average consultation time (simplified)
        avg_time = db.execute("""
            SELECT AVG(julianday(seen_time) - AVG(julianday(check_in_time)) as avg_hours
            FROM appointments
            WHERE doctor_id = ? 
            AND seen_time IS NOT NULL
        """, (doctor['doctor_id'],)).fetchone()['avg_hours'] or 0.5  # Default 0.5 hours if no data
        
        # Convert to minutes (simplified calculation)
        wait_minutes = int(pending * avg_time * 60)
        
        wait_times[doctor['name'].lower().replace(' ', '_')] = wait_minutes
    
    return wait_times

@app.route('/')
def home():
    try:
        wait_times = calculate_wait_times()
    except sqlite3.OperationalError:
        # If database isn't initialized, use sample data
        wait_times = {
            'doctor_a': random.randint(5, 30),
            'doctor_b': random.randint(10, 45),
            'doctor_c': random.randint(15, 60)
        }
    
    now = datetime.now().strftime("%H:%M")
    
    return render_template('index.html', 
                         wait_times=wait_times,
                         current_time=now)

@app.route('/add_appointment', methods=['GET', 'POST'])
def add_appointment():
    if request.method == 'POST':
        # Get form data
        patient_name = request.form['patient_name']
        dob = request.form['dob']
        doctor_id = request.form['doctor_id']
        scheduled_time = request.form['scheduled_time']
        
        try:
            db = get_db()
            
            # Insert patient if not exists
            patient = db.execute(
                "SELECT patient_id FROM patients WHERE name = ? AND date_of_birth = ?",
                (patient_name, dob)
            ).fetchone()
            
            if not patient:
                cursor = db.execute(
                    "INSERT INTO patients (name, date_of_birth) VALUES (?, ?)",
                    (patient_name, dob)
                )
                patient_id = cursor.lastrowid
                db.commit()
            else:
                patient_id = patient['patient_id']
            
            # Create appointment
            db.execute(
                "INSERT INTO appointments (patient_id, doctor_id, scheduled_time) VALUES (?, ?, ?)",
                (patient_id, doctor_id, scheduled_time)
            )
            db.commit()
            
            flash('Appointment scheduled successfully!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            flash(f'Error scheduling appointment: {str(e)}', 'error')
    
    # For GET request or if there's an error
    db = get_db()
    doctors = db.execute("SELECT doctor_id, name FROM doctors").fetchall()
    return render_template('add_appointment.html', doctors=doctors)

if __name__ == '__main__':
    app.run(debug=True)