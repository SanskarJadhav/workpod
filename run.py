import streamlit as st
import sqlite3
from PIL import Image
import io

# Function to create SQLite database and table if not exists
def create_database():
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    
    # Check if the users table exists
    c.execute('''SELECT count(name) FROM sqlite_master WHERE type='table' AND name='users' ''')
    if c.fetchone()[0] == 0:
        # Create the new users table
        c.execute('''CREATE TABLE users
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                     username TEXT NOT NULL, 
                     email TEXT NOT NULL, 
                     project_id TEXT NOT NULL,
                     image BLOB)''')
        conn.commit()
    
    conn.close()

# Function to insert user data into the database
def insert_user_data(username, email, project_id, image):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('''INSERT INTO users (username, email, project_id, image) VALUES (?, ?, ?, ?)''',
              (username, email, project_id, image))
    conn.commit()
    conn.close()

# Function to delete records based on project ID
def delete_records_by_project_id(project_id):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('''DELETE FROM users WHERE project_id = ?''', (project_id,))
    conn.commit()
    conn.close()

# Function to retrieve user data based on project ID
def get_users_by_project_id(project_id):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM users WHERE project_id = ?''', (project_id,))
    data = c.fetchall()
    conn.close()
    return data

# Main Streamlit app
def main():
    # Create SQLite database if it doesn't exist
    create_database()

    # Set page title and navigation
    st.set_page_config(page_title="Project Registration", layout="wide", initial_sidebar_state="collapsed")

    # Page navigation
    page = st.sidebar.radio("Navigation", ["Project Registration", "Project Dashboard"])

    if page == "Project Registration":
        st.title("Project Registration")

        # Display form for user input
        project_id = st.text_input("Enter Project ID:")
        username = st.text_input("Enter your username:")
        email = st.text_input("Enter your email:")

        # Image upload
        uploaded_image = st.file_uploader("Upload Profile Image", type=['jpg', 'jpeg', 'png'])

        # Save user data to database upon form submission
        if st.button("Submit"):
            if project_id and username and email:
                if uploaded_image is not None:
                    # Convert uploaded image to bytes
                    image_bytes = uploaded_image.read()
                    insert_user_data(username, email, project_id, image_bytes)
                    st.success("You have successfully registered!")
                    st.session_state.project_id = project_id
                    st.rerun()
                else:
                    st.error("Please upload a profile image.")
            else:
                st.error("Please fill in all the fields.")

    elif page == "Project Dashboard":
        st.title("Project Dashboard")

        # Display user's project ID
        project_id = st.session_state.get("project_id")
        if project_id:
            st.write(f"You are currently working on Project ID: {project_id}")
            # Delete project button
            if st.button("Delete Project", key="delete_button"):
                delete_records_by_project_id(project_id)
                st.success(f"All records for project ID '{project_id}' have been deleted.")

            # Display users with the same project ID
            st.sidebar.header("Active Users")
            project_users = get_users_by_project_id(project_id)
            for user in project_users:
                st.sidebar.write(f"Username: {user[1]}")
                st.sidebar.write(f"Email: {user[2]}")
                if user[4] is not None:
                    # Display uploaded image with smaller size
                    image = Image.open(io.BytesIO(user[4]))
                    st.sidebar.image(image, width=100, caption=user[1])

if __name__ == "__main__":
    main()
