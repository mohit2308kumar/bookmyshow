import mysql.connector
import os
from datetime import datetime

# Connect to the MySQL database
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user=os.getenv("DBUSER"),
        password=os.getenv("DBPASSWD"),
        database=os.getenv("DBNAME")
    )
    
# Function to register a new user
def register_user(username, password, email, phone):
    db = connect_db()
    cursor = db.cursor()
    
    try:
        cursor.execute("INSERT INTO users (username, password, email, phone) VALUES (%s, %s, %s, %s)", (username, password, email, phone))
        db.commit()
        print("User registered successfully.")
    except mysql.connector.Error as err:
        print("Error:", err)
    finally:
        db.close()

# Function to view all available movies
def view_movies():
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM movies")
    movies = cursor.fetchall()
    
    print("\nAvailable Movies:")
    for movie in movies:
        print(f"{movie[0]}: {movie[1]} ({movie[2]}) - {movie[3]} mins [{movie[4]}]")
    
    db.close()

# Function to view shows for a specific movie
def view_shows(movie_id):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT shows.show_id, shows.show_time, theaters.name, theaters.location FROM shows JOIN theaters ON shows.theater_id = theaters.theater_id WHERE movie_id = %s", (movie_id,))
    shows = cursor.fetchall()
    
    print(f"\nAvailable Shows for Movie ID {movie_id}:")
    for show in shows:
        print(f"Show ID: {show[0]}, Theater: {show[2]}, Location: {show[3]}, Time: {show[1]}")
    
    db.close()

# Function to select and book seats
def book_seats(user_id, show_id, seat_ids):
    db = connect_db()
    cursor = db.cursor()
    
    # Check seat availability
    cursor.execute("SELECT seat_id FROM show_seats WHERE show_id = %s AND seat_id IN (%s) AND is_booked = FALSE" % (show_id, ",".join(map(str, seat_ids))))
    available_seats = cursor.fetchall()
    
    if len(available_seats) < len(seat_ids):
        print("Some seats are not available!")
        db.close()
        return

    # Calculate total price based on the number of seats
    cursor.execute("SELECT price FROM shows WHERE show_id = %s", (show_id,))
    show_price = cursor.fetchone()[0]
    total_price = show_price * len(seat_ids)
    
    # Insert booking record
    cursor.execute("INSERT INTO bookings (show_id, user_id, total_price) VALUES (%s, %s, %s)", (show_id, user_id, total_price))
    booking_id = cursor.lastrowid
    
    # Update seat booking status
    for seat_id in seat_ids:
        cursor.execute("UPDATE show_seats SET is_booked = TRUE WHERE show_id = %s AND seat_id = %s", (show_id, seat_id))
        cursor.execute("INSERT INTO booking_details (booking_id, seat_id) VALUES (%s, %s)", (booking_id, seat_id))
    
    # Insert transaction record
    cursor.execute("INSERT INTO transactions (booking_id, amount) VALUES (%s, %s)", (booking_id, total_price))
    db.commit()
    
    print(f"Booking successful! Booking ID: {booking_id}, Total Price: {total_price}")
    
    db.close()

# Function to view bookings for a specific user
def view_bookings(user_id):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT b.booking_id, s.show_time, t.name, t.location, b.total_price 
        FROM bookings b 
        JOIN shows s ON b.show_id = s.show_id 
        JOIN theaters t ON s.theater_id = t.theater_id 
        WHERE b.user_id = %s
    """, (user_id,))
    bookings = cursor.fetchall()
    
    print(f"\nBookings for User ID {user_id}:")
    for booking in bookings:
        print(f"Booking ID: {booking[0]}, Theater: {booking[2]}, Location: {booking[3]}, Show Time: {booking[1]}, Total Price: {booking[4]}")
    
    db.close()

# Main function to interact with the program
def main():
    while True:
        print("\n1. Register User")
        print("2. View Movies")
        print("3. View Shows")
        print("4. Book Seats")
        print("5. View Bookings")
        print("6. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == "1":
            username = input("Enter username: ")
            password = input("Enter password: ")
            email = input("Enter email: ")
            phone = input("Enter phone: ")
            register_user(username, password, email, phone)
        
        elif choice == "2":
            view_movies()
        
        elif choice == "3":
            movie_id = int(input("Enter Movie ID to view shows: "))
            view_shows(movie_id)
        
        elif choice == "4":
            user_id = int(input("Enter your User ID: "))
            show_id = int(input("Enter Show ID: "))
            seat_ids = list(map(int, input("Enter seat IDs to book (comma-separated): ").split(',')))
            book_seats(user_id, show_id, seat_ids)
        
        elif choice == "5":
            user_id = int(input("Enter your User ID to view bookings: "))
            view_bookings(user_id)
        
        elif choice == "6":
            print("Exiting...")
            break
        
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main()

