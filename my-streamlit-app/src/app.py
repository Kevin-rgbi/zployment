import streamlit as st

def main():
    st.set_page_config(page_title="My Streamlit App", layout="wide")
    
    st.title("Welcome to My Streamlit App")
    st.sidebar.title("Navigation")
    
    # Add navigation options here
    page = st.sidebar.radio("Go to", ["Home", "Other Page"], key="nav_page")
    
    if page == "Home":
        from pages.home import display_home
        display_home()
    else:
        st.write("This is another page.")


if __name__ == "__main__":
    main()