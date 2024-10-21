from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from geopy.distance import geodesic
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/after_portal'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model
class Helper(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/provide-help', methods=['GET', 'POST'])
def provide_help():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        
        # Save data to database
        new_helper = Helper(name=name, email=email, latitude=latitude, longitude=longitude)
        db.session.add(new_helper)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('provide_help.html')

@app.route('/need-help', methods=['POST'])
def need_help():
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    
    # Fetch all helpers from the database
    helpers = Helper.query.all()
    
    # Calculate distances and find nearby helpers
    nearby_helpers = []
    user_location = (latitude, longitude)
    for helper in helpers:
        helper_location = (helper.latitude, helper.longitude)
        distance = geodesic(user_location, helper_location).meters
        if distance <= 250:
            nearby_helpers.append(helper.email)
    
    # Send email to nearby helpers
    send_email_to_helpers(nearby_helpers, latitude, longitude)
    
    return "Help request sent to nearby helpers!"

def send_email_to_helpers(emails, latitude, longitude):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "your-email@gmail.com"
    sender_password = "your-email-password"
    
    subject = "Medical Help Needed Nearby"
    body = f"Someone nearby needs help. Here is the location: https://maps.google.com/?q={latitude},{longitude}"
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    
    # Connect to SMTP server and send email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        for email in emails:
            msg['To'] = email
            server.sendmail(sender_email, email, msg.as_string())

if __name__ == '__main__':
    app.run(debug=True)
