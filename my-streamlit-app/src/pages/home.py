import streamlit as st

def display_home() -> None:
    st.title("Home")
    st.write("This is the home page of the application.")
    
    st.sidebar.header("Navigation")
    st.sidebar.write("Use the sidebar to navigate through the app.")
    
    st.write("Here you can add your content, visualizations, and widgets.")

if __name__ == "__main__":
    display_home()