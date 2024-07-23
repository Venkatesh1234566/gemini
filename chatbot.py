import streamlit as st
import os
import requests
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import google.generativeai as genai

# Google API key and Custom Search Engine ID
api_key = "AIzaSyCLIkFf7SksG34qUgdO6-3LZQ5uqhJ80RA"  # Replace with your Google API key
cse_id = "b2198b7139fc148a4"  # Replace with your Custom Search Engine ID

# Gemini API key
os.environ["GOOGLE_API_KEY"] = "AIzaSyDWzA4yiBc7amljOYTMnp8yxUgwB6YqGN4"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# Function to search for images
def search_images(query, api_key, cse_id):
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "cx": cse_id,
        "key": api_key,
        "searchType": "image",
        "num": 2  # Limit to 2 images
    }

    response = requests.get(search_url, params=params)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        st.error(f"HTTP error occurred: {err}")
        st.error(f"Response text: {response.text}")
        return None

    return response.json()

# Function to display images
def display_images(search_results):
    if not search_results or 'items' not in search_results:
        st.warning("No images found or there was an error.")
        return

    cols = st.columns(2)  # Create two columns for displaying images
    for i, item in enumerate(search_results['items']):
        image_url = item['link']
        try:
            response = requests.get(image_url)
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            cols[i % 2].image(img, use_column_width=True)
        except UnidentifiedImageError:
            st.warning(f"Cannot identify image from URL: {image_url}")
        except requests.exceptions.RequestException as e:
            st.error(f"Request error for URL {image_url}: {e}")

# Function to generate text using Gemini model
def generate_text(prompt):
    inputs = [prompt]
    response = model.generate_content(inputs, stream=True)
    response.resolve()
    return response.text if response else "Failed to generate text."

# Initialize session state for storing chat history
if 'history' not in st.session_state:
    st.session_state.history = []

# Streamlit app
st.title("Teach Me ChatBot")

# Display chat history
for entry in st.session_state.history:
    if "user" in entry:
        st.markdown(f"**🧑🏻‍💻:** {entry['user']}")
    if "images" in entry:
        st.markdown("**🤖:** Here are some images I found:")
        display_images(entry["images"])
    if "bot" in entry:
        st.markdown(f"{entry['bot']}")
    if "error" in entry:
        st.error(entry["error"])

# Form for user input
with st.form(key='input_form', clear_on_submit=True):
    query = st.text_input("Enter a search term:", key="input_box")
    submitted = st.form_submit_button("Send")

    if submitted and query:
        # Fetch and display images
        search_results = search_images(query, api_key, cse_id)
        if search_results:
            st.session_state.history.append({"user": query})
            st.session_state.history.append({"images": search_results})
        else:
            st.session_state.history.append({"user": query})
            st.session_state.history.append({"error": "Failed to fetch search results."})

        # Generate and display text
        generated_text = generate_text(query)
        st.session_state.history.append({"bot": generated_text})
        
        st.experimental_rerun()
