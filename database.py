from flask import request
import os
import pyodbc
import pandas as pd
from pydantic import BaseModel


# drop table users

# create table users (id int identity(1,1) primary key,username varchar(50),email varchar(100),password varchar(max),ispremium varchar(10) default 'false')

# SERVER='DESKTOP-363P3OQ\\SQLEXPRESS'
# DATABASE='tourism'
# connectionString = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE}; Trusted_Connection=yes;'
# conn = pyodbc.connect(connectionString)

SERVER = 'LAPTOP-HFEJ7A77\\MSSQLSERVER01'
DATABASE = 'tourism'
connectionString = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'
conn = pyodbc.connect(connectionString)

# id=None
# ses_user=None

# def getData(session_user):
#     id=getID(session_user)
#     if not isinstance(id, int):
#         id = int(id)  # Convert to integer if necessary
#     select_query = "SELECT cities FROM dbo.weather WHERE uid = ?"
#     df = pd.read_sql(select_query, conn, params=[id])
#     cities = df['cities'].tolist()
#     return cities
    

    
# def getID(ses_user):
#     select_query = f"SELECT id FROM dbo.users WHERE username = '{ses_user}'"
#     df = pd.read_sql(select_query, conn)
#     if not df.empty:
#         id = df['id'].iloc[0]  # Extract the first password from the Series
#         return id
        

# def insert_city(current_user,new_city):
#     id=getID(current_user)
#     cursor = conn.cursor()
#     cursor.execute("INSERT INTO dbo.weather (cities, uid) VALUES (?, ?)", (new_city,str(id)))
#     conn.commit()

# def get_premuim(session_user):
#     ses_user=session_user
#     id=getID(ses_user)
#     if not isinstance(id, int):
#         id = int(id)  # Convert to integer if necessary
#     select_query = "SELECT ispremium FROM dbo.users WHERE id = ?"
#     df = pd.read_sql(select_query, conn, params=[id])
#     if not df.empty:
#         premuim = df['ispremium'].iloc[0]
#         if premuim=="true":
#             return True
#         return False
#     return False
                  


#def delete_city(city):
#    cursor = conn.cursor()
#    cursor.execute("delete from dbo.weather where (cities) = (?)", city) 
#    conn.commit()
    
def getUsers():
    select_query = 'select * from dbo.users'
    df = pd.read_sql(select_query, conn)
    users = [users for users in df['email']]
    return users

def getUserName():
    select_query = 'select * from dbo.users'
    df = pd.read_sql(select_query, conn)
    users = [users for users in df['email']]
    return users


def getPassword(email):
    select_query = f"select id,password from dbo.users where email=('{email}')"
    df = pd.read_sql(select_query, conn)
    if not df.empty:
        password = df['password'].iloc[0]  # Extract the first password from the Series
        return password
    

def register_user(new_user_email, new_user_username,new_phone, new_user_password):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO dbo.users (name,email,phone,password) VALUES (?,?,?,?)",new_user_email, new_user_username, new_phone, new_user_password)
    conn.commit()
    return True

def check_user_exists(email):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM dbo.users WHERE email = ?", (email,))
        count = cursor.fetchone()[0]
        return count > 0
    except pyodbc.Error as e:
        print(f"Error: {e}")
        return False
    finally:
        cursor.close()

def update_password(email, new_password):
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE dbo.users SET password = ? WHERE email = ?", (new_password, email))
        conn.commit()
        return True
    except pyodbc.Error as e:
        print(f"Error: {e}")
        return False
    finally:
        cursor.close()

def getuser_by_email(email):
    cursor = conn.cursor()
    query = "SELECT Name, Email, Phone FROM Users WHERE Email = ?"
    cursor.execute(query, (email,))
    user = cursor.fetchone()
    cursor.close()

    if user:
        return {
            'name': user[0],
            'email': user[1],
            'phone': user[2]
        }
    return None


def insert_destination(tour_name, prize, days, location, nearby, image_path):
    print(image_path)
    try:
        # Assuming 'conn' is a global or passed database connection object
        cursor = conn.cursor()

        # SQL query with placeholders
        query = "INSERT INTO Destinations (TourName, Prize, DaysOfTour, Location, NearbyAttractions, Image) VALUES (?, ?, ?, ?, ?, ?)"
        
        
        # Execute the query with the provided parameters
        cursor.execute(query, (tour_name, prize, days, location, nearby, image_path))
        conn.commit()
        
        print("Destination added to database successfully!")  # Debug print
        return True  # Return success flag
    
    except Exception as e:
        print(f"Error inserting destination: {e}")
        conn.rollback()
        return False  # Return failure flag

    finally:
        cursor.close() 

def get_all_destinations():
    cursor = conn.cursor()
    # Use correct column names here
    query = "SELECT DestinationID, TourName, Prize, DaysOfTour, Location, NearbyAttractions, Image FROM Destinations"
    cursor.execute(query)
    destinations = cursor.fetchall()
    cursor.close()
    return destinations

# Function to fetch user details by user ID or email
def get_user_by_email(email):
    cursor = conn.cursor()
    query = "SELECT id, name, phone FROM dbo.users WHERE Email = ?"
    cursor.execute(query, (email))
    user = cursor.fetchone()
    cursor.close()
    print("user")
    if user:
        return {
            'id': user[0],
            'name': user[1],
            'phone': user[2]
        }
    
    return None

# Function to fetch destination details by DestinationID
def get_destination_by_id(destination_id):
    cursor = conn.cursor()
    query = "SELECT DestinationID, TourName, Prize, DaysOfTour, Location, NearbyAttractions, Image FROM Destinations WHERE DestinationID = ?"
    cursor.execute(query, (destination_id,))
    destination = cursor.fetchone()  # Fetch the result
    cursor.close()

    if destination:
        # Return a dictionary with the correct keys matching your column names
        return {
            'DestinationID': destination[0],
            'TourName': destination[1],
            'Prize': destination[2],
            'DaysOfTour': destination[3],
            'Location': destination[4],
            'NearbyAttractions': destination[5],
            'Image': destination[6]
        }
    return None


# Function to insert a new booking
def add_booking(Id, Name, Phone, destination_id, tour_name, prize):
    cursor = conn.cursor()
    try:
        query = "INSERT INTO Booking (id, name, phone, DestinationID, TourName, Prize, BookingDate) VALUES (?, ?, ?, ?, ?, ?, GETDATE())"
        cursor.execute(query, (Id, Name, Phone, destination_id, tour_name, prize))
        conn.commit()
        return True  # Return success flag
    except Exception as e:
        print(f"Error adding booking: {e}")
        conn.rollback()
        return False  # Return failure flag
    finally:
        cursor.close()

def get_booking_data():
    cursor = conn.cursor()
    query = "SELECT * FROM Booking"
    cursor.execute(query)
    data = cursor.fetchall()
    #conn.close()
    cursor.close() 
    return data

def delete_booking_from_db(booking_id):
    cursor = conn.cursor()
    query = "DELETE FROM Booking WHERE BookingID = ?"
    cursor.execute(query, (booking_id,))
    conn.commit()
    #conn.close()
    cursor.close()

def delete_destination(destination_id):
    cursor = conn.cursor()
    query = "DELETE FROM Destinations WHERE DestinationID = ?"
    cursor.execute(query, (destination_id,))
    conn.commit()
    cursor.close()

def update_destination(destination_id, tour_name, prize, days, location, nearby, image_path=None):
    cursor = conn.cursor()
    try:
        if image_path:
            query = "UPDATE Destinations SET TourName=?, Prize=?, DaysOfTour=?, Location=?, NearbyAttractions=?, Image=? WHERE DestinationID=?"
            cursor.execute(query, (tour_name, prize, days, location, nearby, image_path, destination_id))
        else:
            query = "UPDATE Destinations SET TourName=?, Prize=?, DaysOfTour=?, Location=?, NearbyAttractions=? WHERE DestinationID=?"
            cursor.execute(query, (tour_name, prize, days, location, nearby, destination_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating destination: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def get_image_data(destination_id):
    cursor = conn.cursor()
    query = "SELECT Images FROM Destinations WHERE DestinationID = ?"
    cursor.execute(query, (destination_id,))
    result = cursor.fetchone()
    cursor.close()
    if result:
        return result[0]  # Return image data
    return None

def insert_enquiry(name, email, description):
    cursor = conn.cursor()
    query = "INSERT INTO GuestEnquiries (Name, Email, Description) VALUES (?, ?, ?)"
    cursor.execute(query, (name, email, description))
    conn.commit()
    cursor.close()

def get_all_enquiries():
    cursor = conn.cursor()
    query = "SELECT EnquiryID, Name, Email, Description,SubmittedAt FROM GuestEnquiries"
    cursor.execute(query)
    enquiries = cursor.fetchall()
    return enquiries

def delete_enquiry(enquiry_id):
    cursor = conn.cursor()
    query = "DELETE FROM GuestEnquiries WHERE EnquiryID = ?"
    cursor.execute(query, (enquiry_id,))
    conn.commit()

def get_all_users():
    cursor = conn.cursor()
    query = "SELECT * FROM dbo.users"
    cursor.execute(query)
    users = cursor.fetchall()
    cursor.close()
    return users

def delete_user(user_id):
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM dbo.users WHERE id = ?", (user_id,))
        conn.commit()
    except pyodbc.Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()

