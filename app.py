from flask import Flask, render_template, request, redirect, url_for, session, make_response
from functools import wraps
import functions
import database
import os


app = Flask(__name__)
app.secret_key = 'your_secret_key' 

@app.after_request
def add_no_cache(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# Block 2: Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['POST', 'GET'])
@app.route('/home', methods=['POST', 'GET'])
def homePage():
    if request.method == 'POST':
        result = functions.add_enquiry(request)
        return render_template('home.html', msg="")
    
    return render_template('home.html')

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        value = functions.login_user()

        if value == 'not':
            return render_template('Login.html', msg="Username does not exist")
        
        print("hello world", value)

        if value == "admin":
            # Redirect or render a page specific for admin
            print("admin")
            return redirect(url_for('adminhome'))  # Replace 'admin_dashboard' with your admin page/route
        
        if value == "tuser":
            return redirect(url_for('index'))  # Redirect to the user homepage
        
        # If passwords are incorrect or any other case
        return render_template('Login.html', msg="Incorrect username or password")

    # GET request, render login page
    return render_template('Login.html', msg="")



@app.route("/index",methods=['POST','GET'])
@login_required  
def index():

    return render_template('index.html',msg=" ")


@app.route("/adminhome",methods=['POST','GET'])
@login_required
def adminhome():
    destinations = database.get_all_destinations()
    return render_template('adminhome.html',msg=" ", destinations=destinations)


@app.route("/register",methods=['POST','GET'])
def register():
    if request.method == 'POST':
        value=functions.register_func()   
        if value=='not match':
            return render_template('register.html', msg=" password not matched")   
        if not value:
            return render_template('register.html',msg="User already exist")
       
        return redirect('/login')

    return render_template('register.html', msg="")

@app.route("/about",methods=['POST','GET'])
def about():
    return render_template('about.html')

@app.route("/destination", methods=['POST', 'GET'])
@login_required
def destination():
    destinations = database.get_all_destinations()  # Fetch data from the database
    return render_template('destination.html', destinations=destinations)

@app.route('/book_destination/<int:destination_id>', methods=['POST', 'GET'])
def book_destination(destination_id):
    if 'email' not in session:
        return redirect('/login')  # Redirect to login if not logged in
    
    user_email = session['email']  # Get the logged-in user's email
    user = database.get_user_by_email(user_email)  # Fetch the user details
    destination = database.get_destination_by_id(destination_id)  # Fetch the destination details
    
    if user and destination:
        # Add the booking to the Booking table
        booking_success = database.add_booking(
            user['id'],
            user['name'],
            user['phone'],
            destination['DestinationID'],  # DestinationID (correct key)
            destination['TourName'],  # TourName
            destination['Prize']  # Prize
        )
        return redirect('/destination')  # Redirect after successful booking


# @app.route('/image/<int:destination_id>')
# def serve_image(destination_id):
#     image_data = database.get_image_data(destination_id)
#     if image_data:
#         return send_file(io.BytesIO(image_data), mimetype='image/jpeg')
#     return "Image not found", 404

@app.route("/profile",methods=['POST','GET'])
@login_required
def profile():
    email = functions.session_check()

    if email == "NO":
        return redirect(url_for('login'))  # Redirect to login if the session is not active
    
    # Get the user details by email
    user = database.getuser_by_email(email)  # Assuming you query the user details based on the email
    
    if not user:
        return "User not found", 404

    # Render the profile.html template and pass user details
    return render_template('profile.html', user=user)

@app.route("/contact",methods=['POST','GET'])
def contact():
    return render_template('contact.html')

@app.route("/forgotpassword",methods=['POST','GET'])
def forgotpassword():
    if request.method == 'POST':
        result = functions.forgot_password()
        if result == 'User not found':
            return render_template('forgotpassword.html', msg="User not found")
        return render_template('login.html', msg="Password updated. Please log in with your new password.")
    
    return render_template('forgotpassword.html')

@app.route('/serve_image/<int:destination_id>')
def serve_image(destination_id):
    destination = database.get_destination_by_id(destination_id)
    if destination:
        return redirect('/' + destination['Image'])  # serves from static/images/
    return "Image not found", 404

@app.route('/delete_destination/<int:destination_id>', methods=['POST'])
@login_required
def delete_destination(destination_id):
    database.delete_destination(destination_id)
    return redirect('/adminhome')

@app.route('/edit_destination/<int:destination_id>', methods=['POST'])
@login_required
def edit_destination(destination_id):
    tour_name = request.form['tour_name']
    prize = request.form['prize']
    days = request.form['days']
    location = request.form['location']
    nearby = request.form['nearby']

    image = request.files.get('image')
    image_path = None
    if image and image.filename != '':
        from werkzeug.utils import secure_filename
        image_folder = 'static/images'
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)
        image_filename = secure_filename(image.filename)
        image_path = os.path.join(image_folder, image_filename).replace("\\", "/")
        image.save(image_path)

    database.update_destination(destination_id, tour_name, prize, days, location, nearby, image_path)
    return redirect(url_for('adminhome'))

@app.route('/add_destination', methods=['GET', 'POST'])
@login_required
def add_destination():
    if request.method == 'POST':
        result = functions.add_destination(request)
        return redirect(url_for('adminhome'))

    destinations = database.get_all_destinations()
    return render_template('adminhome.html', destinations=destinations)

@app.route('/adminmanageuser', methods=['GET'])
@login_required
def admin_manage_user():
    users = database.get_all_users()  # Fetch all users
    return render_template('adminmanageuser.html', users=users)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    database.delete_user(user_id)
    return redirect('/adminmanageuser')


@app.route('/adminguestenquiry', methods=['GET'])
@login_required
def admin_guest_enquiry():
    enquiries = database.get_all_enquiries()
    return render_template('adminguestenquiry.html', enquiries=enquiries)

@app.route('/delete_enquiry/<int:enquiry_id>', methods=['POST'])
def delete_enquiry(enquiry_id):
    database.delete_enquiry(enquiry_id)
    return redirect('/adminguestenquiry')

@app.route("/adminmanagebooking",methods=['POST','GET'])
@login_required
def admin_manage_booking():
    booking_data = database.get_booking_data()  # Fetch data from the Booking table
    return render_template('adminmanagebooking.html', bookings=booking_data)

# @app.route('/deletebooking/<int:booking_id>', methods=['POST'])
# def delete_booking(booking_id):
#     database.delete_booking_from_db(booking_id)  # Call function to delete booking from database
#     return redirect('/adminmanagebooking')

@app.route('/logout')
def logout():
    functions.logout_user()
    return redirect('/home')
    

if __name__ == '__main__':
    app.run(debug=True)