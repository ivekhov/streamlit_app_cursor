import streamlit as st
import json
import base64
import hashlib
from datetime import datetime, timedelta

def create_session_token(username, is_admin, current_page='default', current_section=None):
    """Create an encoded session token"""
    session_data = {
        "username": username,
        "is_admin": is_admin,
        "current_page": current_page,
        "current_section": current_section,
        "expiry": (datetime.now() + timedelta(days=7)).isoformat()
    }
    
    # Add a salt/secret to increase security
    secret = "streamlit_app_secret_key"
    signature = hashlib.sha256(f"{username}{secret}".encode()).hexdigest()
    session_data["signature"] = signature
    
    # Encode the data
    token_str = json.dumps(session_data)
    return base64.b64encode(token_str.encode()).decode()

def validate_session_token(token):
    """Validate and decode a session token"""
    try:
        if not token:
            return None, None, None, None
        
        # Decode the token
        token_str = base64.b64decode(token).decode()
        session_data = json.loads(token_str)
        
        # Check if session is expired
        expiry = datetime.fromisoformat(session_data["expiry"])
        if datetime.now() > expiry:
            return None, None, None, None
        
        # Verify signature
        username = session_data["username"]
        secret = "streamlit_app_secret_key"
        expected_signature = hashlib.sha256(f"{username}{secret}".encode()).hexdigest()
        if session_data.get("signature") != expected_signature:
            return None, None, None, None
        
        # Return username, is_admin, current_page, current_section
        return (
            session_data["username"], 
            session_data["is_admin"],
            session_data.get("current_page", "default"),
            session_data.get("current_section", None)
        )
    except Exception as e:
        print(f"Error validating token: {str(e)}")
        return None, None, None, None

# Create a file-based session store
SESSION_FILE = "session_store.json"

def save_session_to_file(username, is_admin, current_page='default', current_section=None):
    """Save session to file to persist across app restarts"""
    try:
        token = create_session_token(username, is_admin, current_page, current_section)
        with open(SESSION_FILE, 'w') as f:
            json.dump({"token": token}, f)
        return True
    except Exception as e:
        print(f"Error saving session: {e}")
        return False

def load_session_from_file():
    """Load session from file"""
    try:
        import os
        if not os.path.exists(SESSION_FILE):
            return None, None, None, None
            
        with open(SESSION_FILE, 'r') as f:
            data = json.load(f)
            token = data.get("token")
            if token:
                return validate_session_token(token)
        return None, None, None, None
    except Exception as e:
        print(f"Error loading session: {e}")
        return None, None, None, None

def clear_session_file():
    """Clear the session file"""
    try:
        import os
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
        return True
    except Exception as e:
        print(f"Error clearing session: {e}")
        return False

def restore_session():
    """Restore session from file"""
    if st.session_state.get('authenticated', False):
        return True
        
    username, is_admin, current_page, current_section = load_session_from_file()
    if username:
        st.session_state.authenticated = True
        st.session_state.username = username
        st.session_state.is_admin = is_admin
        st.session_state.current_page = current_page
        st.session_state.current_section = current_section
        print(f"Restored session for user: {username}, admin: {is_admin}, page: {current_page}, section: {current_section}")
        return True
    
    return False

def save_session(username, is_admin, current_page='default', current_section=None):
    """Save session to file"""
    return save_session_to_file(username, is_admin, current_page, current_section)

def clear_session():
    """Clear session"""
    return clear_session_file() 