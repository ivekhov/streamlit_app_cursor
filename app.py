import streamlit as st
import sqlite3
import hashlib
import os

# Page configuration
st.set_page_config(
    page_title="My Streamlit App",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

def hash_password(password):
    """Hash the password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = None
    try:
        db_path = os.path.join(os.getcwd(), 'users.db')
        print(f"Initializing database at: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            is_admin BOOLEAN NOT NULL
        )
        ''')
        conn.commit()
        print("Users table created successfully")
        
        # Check if admin user exists
        cursor.execute('SELECT username FROM users WHERE username = ?', ('admin',))
        if cursor.fetchone() is None:
            # Create admin user with password 'admin123'
            admin_password = 'admin123'
            hashed_password = hash_password(admin_password)
            
            print(f"Creating admin user with password: {admin_password}")
            print(f"Hashed password: {hashed_password}")
            
            cursor.execute('INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)',
                          ('admin', hashed_password, True))
            conn.commit()
            print("Admin user created successfully!")
        
        # Check if test user exists
        cursor.execute('SELECT username FROM users WHERE username = ?', ('user',))
        if cursor.fetchone() is None:
            # Create test user with password 'password'
            test_password = 'password'
            hashed_password = hash_password(test_password)
            
            print(f"Creating test user with password: {test_password}")
            print(f"Hashed password: {hashed_password}")
            
            cursor.execute('INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)',
                          ('user', hashed_password, False))
            conn.commit()
            print("Test user created successfully!")
        
        # List all users in the database
        cursor.execute('SELECT username, is_admin FROM users')
        users = cursor.fetchall()
        print(f"All users in database: {users}")
        
        return True
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        st.error(f"Error initializing database: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()
            print("Database connection closed after initialization")

def verify_user(username, password):
    """Verify user credentials."""
    print(f"Attempting to verify user: {username}")
    st.write(f"Attempting to verify user: {username}")
    
    if not username or not password:
        print("Username or password is empty")
        st.error("Username and password are required")
        return False, False
    
    conn = None
    try:
        # Use absolute path for database file
        db_path = os.path.join(os.getcwd(), 'users.db')
        print(f"Opening database at: {db_path}")
        st.write(f"Opening database at: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # First check if the user exists
        cursor.execute('SELECT password, is_admin FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        
        if result is None:
            print(f"User not found: {username}")
            st.error(f"User not found: {username}")
            
            # List all users for debugging
            cursor.execute('SELECT username FROM users')
            all_users = cursor.fetchall()
            print(f"Available users in database: {all_users}")
            st.write(f"Available users in database: {all_users}")
            
            return False, False
        
        stored_password = result[0]
        is_admin = result[1]
        
        # Hash the provided password
        hashed_password = hash_password(password)
        
        # Debug output
        print(f"Provided password hash: {hashed_password}")
        print(f"Stored password hash: {stored_password}")
        st.write(f"Provided password hash: {hashed_password}")
        st.write(f"Stored password hash: {stored_password}")
        
        # Compare the hashes
        if hashed_password == stored_password:
            print(f"Login successful for user: {username}")
            return True, is_admin
        else:
            print(f"Invalid password for user: {username}")
            st.error("Invalid password")
            return False, False
    except Exception as e:
        print(f"Error verifying user: {str(e)}")
        st.error(f"Error verifying user: {str(e)}")
        return False, False
    finally:
        if conn:
            conn.close()

def save_user(username, password, is_admin):
    """Save a new user to the database."""
    print(f"Attempting to save user: {username}, is_admin: {is_admin}")
    
    if not username or not password:
        st.error("Username and password are required")
        return False
    
    conn = None
    try:
        # Connect to the database using absolute path
        db_path = os.path.join(os.getcwd(), 'users.db')
        print(f"Opening database at: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if user already exists
        print(f"Checking if user '{username}' already exists...")
        cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            st.error(f"Username '{username}' already exists")
            return False
        
        # Hash the password
        hashed_password = hash_password(password)
        print(f"Hashed password: {hashed_password}")
        
        # Insert the new user
        print(f"Executing INSERT for user: {username}")
        cursor.execute('INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)',
                      (username, hashed_password, is_admin))
        
        # Commit the transaction
        conn.commit()
        print(f"Transaction committed for user: {username}")
        
        # Verify the user was created
        cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        
        if result:
            print(f"User '{username}' successfully created and verified in database")
            return True
        else:
            print(f"Failed to verify user '{username}' after commit")
            st.error(f"Failed to create user '{username}': Verification failed after commit")
            try: conn.rollback() 
            except: pass
            return False
            
    except sqlite3.Error as e:
        print(f"SQLite error saving user: {str(e)}")
        st.error(f"SQLite error saving user: {str(e)}")
        if conn:
            try: 
                conn.rollback()
                print("Transaction rolled back due to SQLite error")
            except Exception as rollback_err:
                 print(f"Error during rollback: {rollback_err}")
        return False
    except Exception as e:
        print(f"Unexpected error saving user: {str(e)}")
        st.error(f"Error saving user: {str(e)}")
        if conn:
            try: 
                conn.rollback()
                print("Transaction rolled back due to unexpected error")
            except Exception as rollback_err:
                 print(f"Error during rollback: {rollback_err}")
        return False
    finally:
        if conn:
            conn.close()
            print(f"Database connection closed after save_user for {username}")

def update_user_password(username, new_password):
    """Update user's password."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    try:
        # Hash the new password
        hashed_password = hash_password(new_password)
        
        # Update the password
        cursor.execute('UPDATE users SET password = ? WHERE username = ?',
                      (hashed_password, username))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error updating password: {str(e)}")
        return False
    finally:
        conn.close()

def get_all_users():
    """Get all users except admin."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT username, is_admin FROM users WHERE username != "admin"')
        users = cursor.fetchall()
        
        # Debug output
        st.write(f"Found {len(users)} users in the database")
        
        return users
    except Exception as e:
        st.error(f"Error retrieving users: {str(e)}")
        return []
    finally:
        conn.close()

def login_page():
    """Display the login page."""
    st.title("🔐 Login")
    
    # Display login instructions
    st.info("Login with admin credentials: username: admin, password: admin123")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if not username or not password:
                st.error("Please enter both username and password")
            else:
                st.write(f"Attempting to login with username: {username}")
                
                is_valid, is_admin = verify_user(username, password)
                if is_valid:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.is_admin = is_admin
                    st.success(f"Login successful! Welcome {username}")
                    st.rerun()
                else:
                    # Error message is already displayed in verify_user function
                    pass

def admin_page():
    """Display the admin page for user management."""
    st.title("👨‍💼 Admin Panel")
    
    # Create new user section using a form
    st.subheader("Create New User")
    
    with st.form(key="create_user_form", clear_on_submit=True):
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        is_admin = st.checkbox("Admin privileges")
        create_user_submitted = st.form_submit_button("Create User")
        
        if create_user_submitted:
            if not new_username or not new_password:
                st.error("Please enter both username and password")
            else:
                st.write(f"Attempting to create user: {new_username}")
                success = save_user(new_username, new_password, is_admin)
                
                if success:
                    st.success(f"User '{new_username}' created successfully!")
                    # Refresh the page to show the updated user list
                    st.rerun()
                # No else needed here, save_user displays errors

    # Update user password section
    st.subheader("Update User Password")
    
    # Get all users except admin
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM users WHERE username != "admin"')
    users = [user[0] for user in cursor.fetchall()]
    conn.close()
    
    if users:
        selected_user = st.selectbox("Select User", users, key="selected_user")
        update_new_password = st.text_input("New Password", type="password", key="update_password")
        
        if st.button("Update Password", key="update_pwd_btn"):
            if not update_new_password:
                st.error("Please enter a new password")
            else:
                success = update_user_password(selected_user, update_new_password)
                if success:
                    st.success(f"Password updated for {selected_user}")
                    # Refresh to show updated data
                    st.rerun()
                else:
                    st.error(f"Failed to update password for {selected_user}")
    else:
        st.info("No non-admin users to manage")
    
    # Display all users table
    st.subheader("All Users")
    
    # Button to refresh user list table
    if st.button("Refresh List", key="refresh_list_btn"):
        st.rerun()
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT username, is_admin FROM users WHERE username != "admin"')
        all_users = cursor.fetchall()
        
        if all_users:
            user_data = []
            for username, is_admin_flag in all_users:
                user_data.append({
                    "Username": username,
                    "Admin": "Yes" if is_admin_flag else "No"
                })
            st.dataframe(user_data)
        else:
            st.info("No non-admin users found in the database")
    except Exception as e:
        st.error(f"Error retrieving users: {str(e)}")
    finally:
        conn.close()

def section1_page():
    """Content for Section 1."""
    st.title("Section 1")
    st.write("This is the content of Section 1")
    
    # Add your section 1 content here
    st.write("Welcome to Section 1!")
    st.write("This is a sample page with some content.")

def section2_page():
    """Content for Section 2."""
    st.title("Section 2")
    st.write("This is the content of Section 2")
    
    # Add your section 2 content here
    st.write("Welcome to Section 2!")
    st.write("This is another sample page with different content.")

def main():
    """Main application logic."""
    # Initialize database
    db_initialized = init_db()
    
    if not db_initialized:
        st.error("Failed to initialize database. Application may not function correctly.")
    
    # Initialize page state if not present
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'default'
    
    # Show login page if not authenticated
    if not st.session_state.authenticated:
        login_page()
        return
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.is_admin = False
        st.session_state.current_page = 'default'
        st.rerun()
    
    # User info
    st.sidebar.write(f"Logged in as: {st.session_state.username}")
    
    # Admin panel button
    if st.session_state.is_admin:
        st.sidebar.markdown("---")
        if st.sidebar.button("Admin Panel"):
            st.session_state.current_page = 'admin'
            st.rerun()
    
    # Section navigation
    st.sidebar.markdown("---")
    st.sidebar.header("Sections")
    
    # Only show section selection if not in admin page
    if st.session_state.current_page != 'admin':
        section = st.sidebar.radio("Select Section", ["Section 1", "Section 2"])
        
        if section == "Section 1":
            section1_page()
        else:
            section2_page()
    else:
        # Display admin page
        admin_page()
        
        # Back button
        if st.sidebar.button("Back to Main"):
            st.session_state.current_page = 'default'
            st.rerun()

if __name__ == "__main__":
    main() 