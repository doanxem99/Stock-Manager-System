# Use for manage user data
import re
from werkzeug.security import generate_password_hash, check_password_hash

class UserManager:
    def __init__(self, db):
        self.db = db

    def hash_function(self, password):
        return generate_password_hash(password)
    
    def check_password(self, password, hash):
        return check_password_hash(hash, password)

    def valid_input(self, email, password):
        error_email = self.valid_email(email)
        error_password = self.valid_password(password)
        if error_email is not None:
            return error_email
        if error_password is not None:
            return error_password
        return None
    
    def valid_email(self, email):
        if email is None:
            return "Email is required"
        if re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None and len(email) <= 255:
            return None
        return "Invalid email address"
    
    def valid_password(self, password):
        if password is None:
            return "Password is required"
        if len(password) >= 8 and len(password) <= 255:
            return None
        return "Password must be between 8 and 255 characters"
    

    def validate_user(self, email, password):
        error = self.valid_input(email, password)  
        if error is not None:
            return error, None
        cur = self.db.connection.cursor()
        cur.execute("SELECT * FROM accounts WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        print(user)
        print(password)
        if user is None or not self.check_password(password, user[1]):
            return "Invalid email or password", None
        return None, user
    
    def insert_user(self, email, password, name):
        error = self.valid_input(email, password)
        if error is not None:
            return error
        cur = self.db.connection.cursor()
        cur.execute("SELECT * FROM accounts WHERE email = %s", (email,))
        user = cur.fetchone()
        if user is not None:
            return "Email already exists"
        password = str(self.hash_function(password))
        cur.execute("INSERT INTO accounts (email, password, name, investment_amount) VALUES (%s, %s, %s, 0)", (email, password, name))
        self.db.connection.commit()
        cur.close()
        return None
    
        