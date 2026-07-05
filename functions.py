import requests #pip install requests
import os
import database
import datetime
from flask import request,session
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

def session_check():
    if 'email' not in session:
        return "NO"
    return session['email']

def checkPremuim():
    value=database.get_premuim(session['email'])
    return value



def register_func():
    username = request.form['username']
    email = request.form['email']
    phone=request.form['phone']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    users=database.getUsers()
    if email in users:
        return False
    if password != confirm_password:
        return 'not match'
    database.register_user(username,email,phone,password)
    
    return True



def login_user():
    email = request.form['email']
    password = request.form['password']

    # Fetch all usernames from the database
    users = database.getUserName()

    # Check if the email exists in the database
    if email not in users:
        return "not"
    
    # Get the stored password from the database for the provided email
    stored_password = database.getPassword(email)

    # Check for admin
    if email == 'sathwika695@gmail.com':
        if password == stored_password:
            session['email'] = email  # Set email in session for admin
            return "admin"
        else:
            return "invalid_admin_password"
    
    # Check for non-admin users
    if email != 'sathwika695@gmail.com':
        if password == stored_password:
            session['email'] = email  # Set email in session for regular users
            return "tuser"
        else:
            return "invalid_tuser_password"
    
    # Passwords don't match, deny login
    return False

def forgot_password():
    email = request.form['email']
    new_password = request.form['new_password']

    # Check if the email exists in the database
    if not database.check_user_exists(email):
        return 'User not found'

    # Update the password
    if database.update_password(email, new_password):
        return 'Password updated successfully'
    else:
        return 'Failed to update password'
    
def add_destination(request):
    # Get form fields
    tour_name = request.form['tour_name']
    prize = request.form['prize']
    days = request.form['days']
    location = request.form['location']
    nearby = request.form['nearby']
    
    # Get the image file from the request
    image = request.files.get('image')
    
    if image and image.filename != '':
        # Define the path where the image will be saved (use forward slashes)
        image_folder = 'static/images'
        
        # Ensure the image folder exists
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)
        
        # Secure the filename and save the image
        image_filename = secure_filename(image.filename)
        image_path = os.path.join(image_folder, image_filename)
        
        # Replace any backslashes with forward slashes for consistent web path usage
        image_path = image_path.replace("\\", "/")
        
        # Save the image file to the folder
        try:
            image.save(image_path)
            print(f"Image saved at: {image_path}")  # Debug print
        except Exception as e:
            print(f"Error saving image: {e}")
        
        # Store the image path in the database
        try:
            result = database.insert_destination(tour_name, prize, days, location, nearby, image_path)
            print(f"Database insertion result: {result}")
        except Exception as e:
            print(f"Error inserting into database: {e}")
        
        return "Destination added successfully!"
    else:
        return "No image file provided or file is invalid."


def add_enquiry(request):
    name = request.form['name']
    email = request.form['email']
    description = request.form['description']

    # Insert the enquiry into the database
    database.insert_enquiry(name, email, description)

    return "enquiry added successfully!"

# def get_guest_enquiries():
#     try:
#         # Retrieve guest enquiries from the database
#         enquiries = database.fetch_guest_enquiries()
#         return enquiries
#     except Exception as e:
#         print(f"Error: {e}")
#         return []


def logout_user():
    session.clear()
    return True

def send_contact_email(name, email, subject, message):
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    sender_email = os.environ.get('SMTP_SENDER_EMAIL', 'vaishnavinaik741@gmail.com')
    sender_password = os.environ.get('SMTP_SENDER_PASSWORD', 'keem fthu ogkn iyec').replace(" ", "")
    receiver_email = 'vaishnavinaik741@gmail.com'

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = f"Contact Form: {subject}"

    body = f"Name: {name}\nEmail: {email}\nSubject: {subject}\n\nMessage:\n{message}"
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        return True, "Your message has been sent successfully!"
    except Exception as e:
        print(f"Error sending email: {e}")
        return False, f"Failed to send email: {e}"

def handle_contact_form(request):
    name = request.form.get('Name')
    email = request.form.get('Email')
    subject = request.form.get('Subject')
    message = request.form.get('Message')

    description = f"Subject: {subject}\n\n{message}"
    db_saved = False
    try:
        database.insert_enquiry(name, email, description)
        db_saved = True
    except Exception as e:
        print(f"Error inserting contact to database: {e}")

    success, email_msg = send_contact_email(name, email, subject, message)
    if success:
        return email_msg
    else:
        if db_saved:
            return "Message received! (saved to database, but failed to send email. Check App Password)"
        else:
            return "Failed to process message."
