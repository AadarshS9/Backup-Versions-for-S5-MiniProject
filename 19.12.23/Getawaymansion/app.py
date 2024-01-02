
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import mysql.connector
from datetime import datetime as dt
from flask import json

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'hotel'
app.config['TEMPLATES_AUTO_RELOAD'] = True

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'getawaymansion'

# Set the timeout value in seconds (adjust as needed)
app.config['MYSQL_CONNECT_TIMEOUT'] = 60000

mysql = MySQL(app)
bcrypt = Bcrypt(app)

with app.app_context():
    cur = mysql.connection.cursor()

    cur.execute("CREATE DATABASE IF NOT EXISTS getawaymansion")
    cur.execute("USE getawaymansion")

    # Drop the tables in the following order
    cur.execute("DROP TABLE IF EXISTS cancellation")
    cur.execute("DROP TABLE IF EXISTS payments")
    cur.execute("DROP TABLE IF EXISTS roomallocation")
    cur.execute("DROP TABLE IF EXISTS booking")
    cur.execute("DROP TABLE IF EXISTS travelplan")
    cur.execute("DROP TABLE IF EXISTS rooms")
    cur.execute("DROP TABLE IF EXISTS customer")
    cur.execute("DROP TABLE IF EXISTS users")


    # Create user table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            userid INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(60) NOT NULL,
            role ENUM('Admin', 'Customer') NOT NULL,
            status ENUM('Active', 'Inactive') NOT NULL
        )
    """)

    # Create rooms table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            roomsid INT AUTO_INCREMENT PRIMARY KEY,
            type VARCHAR(50) NOT NULL,
            rate INT NOT NULL,
            adultcount INT NOT NULL,
            childrencount INT NOT NULL
        )
    """)

    # Create customer table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS customer (
            custid INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(10) NOT NULL,
            firstname VARCHAR(50) NOT NULL,
            lastname VARCHAR(50) NOT NULL,
            email VARCHAR(50) NOT NULL,
            phoneno VARCHAR(20) NOT NULL,
            country VARCHAR(50) NOT NULL,
            city VARCHAR(50) NOT NULL,
            ssn BIGINT NOT NULL,
            userid INT NOT NULL,
            FOREIGN KEY (userid) REFERENCES users(userid)
        )
    """)

    # Create booking table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS booking (
            bookingid INT AUTO_INCREMENT PRIMARY KEY,
            checkindate DATETIME NOT NULL,
            checkoutdate DATETIME NOT NULL,
            status VARCHAR(50) NOT NULL,
            duration INT NOT NULL,
            roomsid INT NOT NULL,
            custid INT NOT NULL,
            FOREIGN KEY (custid) REFERENCES customer(custid),
            FOREIGN KEY (roomsid) REFERENCES rooms(roomsid)
        )
    """)


    
     # Create Payments table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            paymentid INT AUTO_INCREMENT PRIMARY KEY,
            paymenttype VARCHAR(50) NOT NULL,
            amount INT NOT NULL,
            status VARCHAR(50) NOT NULL,
            completed BOOLEAN NOT NULL,
            bookingid INT NOT NULL,
            custid INT NOT NULL,
            FOREIGN KEY (bookingid) REFERENCES booking(bookingid),
            FOREIGN KEY (custid) REFERENCES customer(custid)
        )
    """)

    # Create Cancellation table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cancellation (
            cancellationid INT AUTO_INCREMENT PRIMARY KEY,
            date DATE NOT NULL,
            time TIME NOT NULL,
            paymentid INT NOT NULL,
            bookingid INT NOT NULL,
            custid INT NOT NULL,
            FOREIGN KEY (paymentid) REFERENCES payments(paymentid),
            FOREIGN KEY (bookingid) REFERENCES booking(bookingid),
            FOREIGN KEY (custid) REFERENCES customer(custid)
        )
    """)

    # Create RoomAllocation table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS roomallocation (
            roomallocationid INT AUTO_INCREMENT PRIMARY KEY,
            roomsid INT NOT NULL,
            bookingid INT NOT NULL,
            FOREIGN KEY (roomsid) REFERENCES rooms(roomsid),
            FOREIGN KEY (bookingid) REFERENCES booking(bookingid)
        )
    """)

    # Create TravelPlan table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS TravelPlan (
            travelplanid INT AUTO_INCREMENT PRIMARY KEY,
            preferences VARCHAR(255) NOT NULL,
            radius INT NOT NULL,
            rating FLOAT,
            link VARCHAR(255),
            custid INT NOT NULL,
            FOREIGN KEY (custid) REFERENCES customer(custid)
        )
    """)
    

    mysql.connection.commit()


    # Insert initial data for users
    users_data = [
        {"email": "admin1@gmail.com", "password": "adminone", "role": "Admin", "status": "Active"},
        {"email": "john.doe@example.com", "password": "password1", "role": "Customer", "status": "Active"},
        {"email": "alice.smith@example.com", "password": "password2", "role": "Customer", "status": "Active"},
        {"email": "michael.johnson@example.com", "password": "password3", "role": "Customer", "status": "Active"},
        {"email": "emily.brown@example.com", "password": "password4", "role": "Customer", "status": "Active"},
        {"email": "robert.miller@example.com", "password": "password5", "role": "Customer", "status": "Active"},
        {"email": "sophia.davis@example.com", "password": "password6", "role": "Customer", "status": "Active"},
        # Add more user data as needed
    ]

    # Insert initial data
    rooms_data = [
        {"type": "Penthouse", "rate": 190, "adultcount": 4, "childrencount": 3},
        {"type": "Penthouse", "rate": 190, "adultcount": 4, "childrencount": 3},
        {"type": "Penthouse", "rate": 190, "adultcount": 4, "childrencount": 3},
        {"type": "Presidential Suite", "rate": 160, "adultcount": 4, "childrencount": 3},
        {"type": "Presidential Suite", "rate": 160, "adultcount": 4, "childrencount": 3},
        {"type": "Presidential Suite", "rate": 160, "adultcount": 4, "childrencount": 3},
        {"type": "Executive Suite", "rate": 130, "adultcount": 4, "childrencount": 3},
        {"type": "Executive Suite", "rate": 130, "adultcount": 4, "childrencount": 3},
        {"type": "Executive Suite", "rate": 130, "adultcount": 4, "childrencount": 3},
        {"type": "Studio", "rate": 90, "adultcount": 3, "childrencount": 3},
        {"type": "Studio", "rate": 90, "adultcount": 3, "childrencount": 3},
        {"type": "Studio", "rate": 90, "adultcount": 3, "childrencount": 3},
        {"type": "Studio", "rate": 90, "adultcount": 3, "childrencount": 3},
        {"type": "Studio", "rate": 90, "adultcount": 3, "childrencount": 3},
        {"type": "Deluxe Room", "rate": 60, "adultcount": 3, "childrencount": 3},
        {"type": "Deluxe Room", "rate": 60, "adultcount": 3, "childrencount": 3},
        {"type": "Deluxe Room", "rate": 60, "adultcount": 3, "childrencount": 3},
        {"type": "Deluxe Room", "rate": 60, "adultcount": 3, "childrencount": 3},
        {"type": "Deluxe Room", "rate": 60, "adultcount": 3, "childrencount": 3},
        {"type": "Standard Room", "rate": 30, "adultcount": 3, "childrencount": 3},
        {"type": "Standard Room", "rate": 30, "adultcount": 3, "childrencount": 3},
        {"type": "Standard Room", "rate": 30, "adultcount": 3, "childrencount": 3},
        {"type": "Standard Room", "rate": 30, "adultcount": 3, "childrencount": 3},
        {"type": "Standard Room", "rate": 30, "adultcount": 3, "childrencount": 3},
        # Add more room data as needed
    ]

    customers_data = [
        {"title": "Mr", "firstname": "John", "lastname": "Doe", "email": "john.doe@example.com", "phoneno": "1234567890", "country": "USA", "city": "New York", "ssn": 123456789, "userid": 2},
        {"title": "Ms", "firstname": "Alice", "lastname": "Smith", "email": "alice.smith@example.com", "phoneno": "9876543210", "country": "Canada", "city": "Toronto", "ssn": 987654321, "userid": 3},
        {"title": "Dr", "firstname": "Michael", "lastname": "Johnson", "email": "michael.johnson@example.com", "phoneno": "5551112233", "country": "UK", "city": "London", "ssn": 555111223, "userid": 4},
        {"title": "Mrs", "firstname": "Emily", "lastname": "Brown", "email": "emily.brown@example.com", "phoneno": "9998887777", "country": "Australia", "city": "Sydney", "ssn": 999888777, "userid": 5},
        {"title": "Mr", "firstname": "Robert", "lastname": "Miller", "email": "robert.miller@example.com", "phoneno": "1112223333", "country": "Germany", "city": "Berlin", "ssn": 111222333, "userid": 6},
        {"title": "Ms", "firstname": "Sophia", "lastname": "Davis", "email": "sophia.davis@example.com", "phoneno": "7776665555", "country": "France", "city": "Paris", "ssn": 777666555, "userid": 7},
        # Add more customer data as needed
    ]

    # Sample data for bookings
    booking_data = [
        {"checkindate": "2023-12-21", "checkoutdate": "2023-12-30", "status": "confirmed", "duration": 9, "roomsid": 1, "custid": 1},
        {"checkindate": "2023-12-15", "checkoutdate": "2023-12-22", "status": "confirmed", "duration": 7, "roomsid": 2, "custid": 2},
        {"checkindate": "2023-12-05", "checkoutdate": "2023-12-15", "status": "pending", "duration": 10, "roomsid": 3, "custid": 3},
        {"checkindate": "2023-12-12", "checkoutdate": "2023-12-20", "status": "confirmed", "duration": 8, "roomsid": 4, "custid": 4},
        {"checkindate": "2023-12-01", "checkoutdate": "2023-12-10", "status": "pending", "duration": 9, "roomsid": 5, "custid": 5},
        {"checkindate": "2023-12-18", "checkoutdate": "2023-12-28", "status": "confirmed", "duration": 10, "roomsid": 6, "custid": 6},
        # Add more booking data as needed
    ]

    # Sample data for payments
    payments_data = [
        {"paymenttype": "Credit Card", "amount": 500, "status": "completed", "completed": True, "bookingid": 1, "custid": 1},
        {"paymenttype": "Debit Card", "amount": 400, "status": "completed", "completed": True, "bookingid": 2, "custid": 2},
        {"paymenttype": "UPI", "amount": 300, "status": "completed", "completed": True, "bookingid": 3, "custid": 3},
        {"paymenttype": "Credit Card", "amount": 450, "status": "completed", "completed": True, "bookingid": 4, "custid": 4},
        {"paymenttype": "Debit Card", "amount": 350, "status": "completed", "completed": True, "bookingid": 5, "custid": 5},
        {"paymenttype": "UPI", "amount": 250, "status": "completed", "completed": True, "bookingid": 6, "custid": 6},
        # Add more payments data as needed
    ]

    # Sample data for cancellations
    cancellation_data = [
        {"date": "2023-12-25", "time": "14:30:00", "paymentid": 1, "bookingid": 1, "custid": 1},
        {"date": "2023-12-18", "time": "10:45:00", "paymentid": 2, "bookingid": 2, "custid": 2},
        # Add more cancellation data as needed
    ]   

    # Sample data for roomallocations
    roomallocation_data = [
        {"roomsid": 1, "bookingid": 1},
        {"roomsid": 2, "bookingid": 2},
        {"roomsid": 3, "bookingid": 3},
        {"roomsid": 4, "bookingid": 4},
        {"roomsid": 5, "bookingid": 5},
        {"roomsid": 6, "bookingid": 6},
        # Add more roomallocation data as needed
    ]

    # Sample data for TravelPlan
    travelplan_data = [
        {"preferences": "Nearby attractions", "radius": 10, "rating": 4.5, "link": "example.com", "custid": 1},
        {"preferences": "Quiet location", "radius": 5, "rating": 4.0, "link": "sample.com", "custid": 2},
        {"preferences": "City center", "radius": 8, "rating": 4.2, "link": "test.com", "custid": 3},
        {"preferences": "Scenic views", "radius": 12, "rating": 4.8, "link": "explore.com", "custid": 4},
        {"preferences": "Beachfront", "radius": 15, "rating": 5.0, "link": "beach.com", "custid": 5},
        {"preferences": "Mountain retreat", "radius": 20, "rating": 4.7, "link": "mountain.com", "custid": 6},
        # Add more travelplan data as needed
    ]

    # Insert sample data into users table
    insert_user_query = "INSERT INTO users (email, password, role, status) VALUES (%s, %s, %s, %s)"
    for user in users_data:
        # Hash the password before storing it
        hashed_password = bcrypt.generate_password_hash(user["password"]).decode('utf-8')
        values = (user["email"], hashed_password, user["role"], "Active")
        cur.execute(insert_user_query, values)

    # Insert sample data into rooms table
    insert_room_query = "INSERT INTO rooms (type, rate, adultcount, childrencount) VALUES (%s, %s, %s, %s)"
    for room in rooms_data:
        values = (room["type"], room["rate"], room["adultcount"], room["childrencount"])
        cur.execute(insert_room_query, values)

    # Insert sample data into customers table
    insert_customer_query = "INSERT INTO customer (title, firstname, lastname, email, phoneno, country, city, ssn, userid) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    for customer in customers_data:
        values = (customer["title"], customer["firstname"], customer["lastname"], customer["email"], customer["phoneno"], customer["country"], customer["city"], customer["ssn"], customer["userid"])
        cur.execute(insert_customer_query, values)

    # Insert sample data into bookings table
    insert_booking_query = "INSERT INTO booking (checkindate, checkoutdate, status, duration, roomsid, custid) VALUES (%s, %s, %s, %s, %s, %s)"
    for booking in booking_data:
        values = (booking["checkindate"], booking["checkoutdate"], booking["status"], booking["duration"], booking["roomsid"], booking["custid"])
        cur.execute(insert_booking_query, values)

    # Insert sample data into payments table
    insert_payment_query = "INSERT INTO payments (paymenttype, amount, status, completed, bookingid, custid) VALUES (%s, %s, %s, %s, %s, %s)"
    for payment in payments_data:
        values = (payment["paymenttype"], payment["amount"], payment["status"], payment["completed"], payment["bookingid"], payment["custid"])
        cur.execute(insert_payment_query, values)

    # Insert sample data into cancellations table
    insert_cancellation_query = "INSERT INTO cancellation (date, time, paymentid, bookingid, custid) VALUES (%s, %s, %s, %s, %s)"
    for cancellation in cancellation_data:
        values = (cancellation["date"], cancellation["time"], cancellation["paymentid"], cancellation["bookingid"], cancellation["custid"])
        cur.execute(insert_cancellation_query, values)

    # Insert sample data into roomallocation table
    insert_roomallocation_query = "INSERT INTO roomallocation (roomsid, bookingid) VALUES (%s, %s)"
    for roomallocation in roomallocation_data:
        values = (roomallocation["roomsid"], roomallocation["bookingid"])
        cur.execute(insert_roomallocation_query, values)

    # Insert sample data into TravelPlan table
    insert_travelplan_query = "INSERT INTO TravelPlan (preferences, radius, rating, link, custid) VALUES (%s, %s, %s, %s, %s)"
    for travelplan in travelplan_data:
        values = (travelplan["preferences"], travelplan["radius"], travelplan["rating"], travelplan["link"], travelplan["custid"])
        cur.execute(insert_travelplan_query, values)
    
    mysql.connection.commit()
    cur.close()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index', methods=['POST'])
def handle_form_submission():
    # Convert string dates to datetime objects for easier comparison
    checkin_date = dt.strptime(request.form['checkin_date'], '%Y-%m-%d').date()
    checkout_date = dt.strptime(request.form['checkout_date'], '%Y-%m-%d').date()
    # Query bookings for the specified dates
    booked_rooms = get_booked_rooms(checkin_date, checkout_date)
    # Query all available rooms
    available_rooms = get_available_rooms()
    # Exclude booked rooms from available rooms
    remaining_rooms = exclude_booked_rooms(available_rooms, booked_rooms)
    # Group remaining rooms by room type
    grouped_rooms = group_rooms_by_type(remaining_rooms)
    # Pass the data to the new template
    return render_template('enquiry.html', grouped_rooms=grouped_rooms, checkin_date=checkin_date, checkout_date=checkout_date)

def get_booked_rooms(checkin_date, checkout_date):
    cursor = mysql.connection.cursor()
    query = """SELECT DISTINCT roomsid FROM booking WHERE checkoutdate > %s AND checkindate < %s"""
    cursor.execute(query, (checkin_date, checkout_date))
    booked_rooms = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return booked_rooms



def get_available_rooms():
    cursor = mysql.connection.cursor()
    query = "SELECT roomsid, type, rate, adultcount, childrencount FROM rooms"
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        available_rooms = [dict(zip(columns, row)) for row in rows]
        # Remove or comment out the debugging print statement in production
        print(available_rooms)
        return available_rooms
    except Exception as e:
        # Handle the exception, log or print the error message
        print(f"Error in get_available_rooms: {e}")
        return []
    finally:
        cursor.close()

def exclude_booked_rooms(available_rooms, booked_rooms):
    remaining_rooms = [room for room in available_rooms if room['roomsid'] not in booked_rooms]
    return remaining_rooms

def group_rooms_by_type(remaining_rooms):
    grouped_rooms = {}
    for room in remaining_rooms:
        room_type = room['type']
        if room_type not in grouped_rooms:
            grouped_rooms[room_type] = []
        grouped_rooms[room_type].append(room)

    return grouped_rooms

@app.route('/explore.html')
def explore():
    return render_template('explore.html')

@app.route('/rooms')
def rooms():
    return render_template('room.html')

@app.route('/room1.html')
def room1():
    return render_template('room1.html')

@app.route('/room2.html')
def room2():
    return render_template('room2.html')

@app.route('/room3.html')
def room3():
    return render_template('room3.html')

@app.route('/room4.html')
def room4():
    return render_template('room4.html')

@app.route('/room5.html')
def room5():
    return render_template('room5.html')

@app.route('/room6.html')
def room6():
    return render_template('room6.html')

@app.route('/aboutus.html')
def aboutus():
    return render_template('aboutus.html')

@app.route('/contactus.html')
def contactus():
    return render_template('contactus.html')



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = 'Customer'  # Set role to 'Customer'
        status = 'Active'  # Set status to 'Active'

        # Check if any of the form fields are empty
        if not email or not password or not confirm_password:
            flash("All fields must be filled.", "error")
            return redirect(url_for('signup'))
        
        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match, try again.', category='error')
            return redirect(url_for('signup'))

        # Check if password is non-empty
        if not password:
            flash("Password must be non-empty. Please fill in a password.", "error")
            return redirect(url_for('signup'))
        
        # Check if password is longer than 4 characters
        if len(password)<4:
            flash("Password must be greater than 4 characters. Please fill in a secure password.", "error")
            return redirect(url_for('signup'))
        
        # Hash the password before storing it
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        try:
            # Check if email already exists
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                flash('Email already exists. Please try again with a different email-id.', category='error')
                return redirect(url_for('signup'))

            # Insert user data into the 'users' table
            cur.execute("""INSERT INTO users (email, password, role, status) VALUES (%s, %s, %s, %s) """, (email, hashed_password, role, status))



            mysql.connection.commit()

            flash('Sign-up successful! Kindly Log in.', category='success')
            return redirect(url_for('signup'))

        except mysql.connector.Error as err:
            # Handle other errors
            print(err)
            flash("An error occurred. Please try again later.", "error")
            return redirect(url_for('signup'))
    cur.close()
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    cur = None  # Initialize the cursor outside the try block

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if email and password are provided
        if not email or not password:
            flash("Email and password are required.", "error")
            return redirect(url_for('login'))

        try:
            cur = mysql.connection.cursor()

            # Check if user exists
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cur.fetchone()

            if user:
                # Check if the provided password matches the hashed password in the database
                if bcrypt.check_password_hash(user[2], password):  # Assuming password hash is at index 2
                    session['user_id'] = user[0]  # Store user ID in the session
                    if user[3] == 'Admin':  # Assuming the role is at index 3
                        return redirect(url_for('admin_dashboard'))
                    elif user[3] == 'Customer':  # Assuming the role is at index 3
                        return redirect(url_for('customer_dashboard'))
                else:
                    flash("Incorrect password. Please try again.", "error")
            else:
                flash("User not found. Please sign up.", "error")

        except Exception as e:
            # Handle the exception, log or print the error message
            print(f"Error in login: {e}")
            flash("An error occurred. Please try again later.", "error")

        finally:
            if cur:
                cur.close()

    return render_template('login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    # Retrieve user details from the database based on user_id
    cur = mysql.connection.cursor()
    cur.execute("SELECT email FROM users WHERE userid = %s", (user_id,))
    user_email = cur.fetchone()[0]
    cur.close()

    return render_template('admin_dashboard.html', user_email=user_email)

@app.route('/customer_dashboard')
def customer_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    # Retrieve user details from the database based on user_id
    cur = mysql.connection.cursor()
    cur.execute("SELECT email FROM users WHERE userid = %s", (user_id,))
    email = cur.fetchone()[0]
    cur.close()

    return render_template('customer_dashboard.html', user_email=email)


@app.route('/logout')
def logout():
    if 'user_id' in session:
        session.pop('user_id')
    return redirect(url_for('index'))






#ADMIN DASHBOARD
@app.route('/admin_view_rooms')
def admin_view_rooms():
    # Check if user is not logged in
    if 'user_id' not in session:
        flash("You must be logged in as an admin to view this page.", "error")
        return redirect(url_for('login'))

    # Check if the user has admin role
    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT role FROM users WHERE userid = %s", (user_id,))
    role = cur.fetchone()[0]
    cur.close()

    if role != 'Admin':
        flash("You must be logged in as an admin to view this page.", "error")
        return redirect(url_for('login'))

    # Fetch all records from the rooms table
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM rooms"
    cursor.execute(query)
    rooms_data = cursor.fetchall()
    cursor.close()

    # Define table headers
    table_headers = ["Room ID", "Type", "Rate", "Adult Count", "Children Count"]

    # Convert room data to list of dictionaries
    rooms_list = []
    for room in rooms_data:
        room_dict = {
            "Room ID": room[0],          # Assuming room ID is at index 0
            "Type": room[1],             # Assuming room type is at index 1
            "Rate": room[2],             # Assuming rate is at index 2
            "Adult Count": room[3],      # Assuming adult count is at index 3
            "Children Count": room[4]    # Assuming children count is at index 4
        }
        rooms_list.append(room_dict)

    # Convert data to JSON for DataTables
    rooms_json = json.dumps(rooms_list)

    return render_template('admin_view_rooms.html', headers=table_headers, rooms_data=rooms_json)

@app.route('/admin_modify_rooms')
def modify_rooms():
    # Implement logic to modify room details
    return render_template('modify_rooms.html')

@app.route('/admin/view_bookings')  
def admin_view_bookings():
    # Check if the user is not logged in
    if 'user_id' not in session:
        flash("You must be logged in as an admin to view this page.", "error")
        return redirect(url_for('login'))

    # Check if the user has admin role
    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT role FROM users WHERE userid = %s", (user_id,))
    role = cur.fetchone()[0]
    cur.close()

    if role != 'Admin':
        flash("You must be logged in as an admin to view this page.", "error")
        return redirect(url_for('login'))

    query = """
        SELECT
                b.bookingid,
                b.checkindate,
                b.checkoutdate,
                b.status,
                b.duration,
                b.roomsid,
                r.type AS room_type,
                b.custid,
                c.firstname,
                c.lastname
            FROM
                booking b
            JOIN
                rooms r ON b.roomsid = r.roomsid
            JOIN
                customer c ON b.custid = c.custid
    """

    cursor = mysql.connection.cursor()
    cursor.execute(query)
    bookings_data = cursor.fetchall()
    cursor.close()

    # Define table headers for bookings, including the new columns
    table_headers = ["Booking ID", "Check-in Date", "Check-out Date", "Status", "Duration", "Room ID",
                     "Room Type", "Customer ID", "Customer Name"]

    # Convert bookings data to list of dictionaries
    bookings_list = []
    for booking in bookings_data:
        booking_dict = {
            "Booking ID": booking[0],
            "Check-in Date": booking[1],
            "Check-out Date": booking[2],
            "Status": booking[3],
            "Duration": booking[4],
            "Room ID": booking[5],
            "Room Type": booking[6],
            "Customer ID": booking[7],
            "Customer Name": f"{booking[8]} {booking[9]}"
        }
        bookings_list.append(booking_dict)

    # Convert data to JSON for DataTables
    bookings_json = json.dumps(bookings_list)

    return render_template('admin_view_bookings.html', headers=table_headers, bookings_data=bookings_json)
@app.route('/admin_view_payments')
def view_payments():
    # Implement logic to fetch and display payment details
    return render_template('view_payments.html')

@app.route('/admin_view_room_allocations')
def view_room_allocations():
    # Implement logic to fetch and display room allocation details
    return render_template('view_room_allocations.html')

@app.route('/admin_view_customers')
def view_customers():
    # Implement logic to fetch and display customer details
    return render_template('view_customers.html')

@app.route('/admin_view_registered_users')
def view_registered_users():
    # Implement logic to fetch and display registered users details
    return render_template('view_registered_users.html')

@app.route('/admin_view_travel_plans')
def view_travel_plans():
    # Implement logic to fetch and display travel plan details
    return render_template('view_travel_plans.html')

@app.route('/admin_view_cancellations')
def view_cancellations():
    # Implement logic to fetch and display cancellation details
    return render_template('view_cancellations.html')

if __name__ == '__main__':
    app.run(debug=True)
