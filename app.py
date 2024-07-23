import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
from PIL import Image, ImageTk
import google.generativeai as genai
import pyautogui
import os
import time

# Set the Google API Key
os.environ["GOOGLE_API_KEY"] = "AIzaSyDWzA4yiBc7amljOYTMnp8yxUgwB6YqGN4"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Function to get a response from Gemini
def get_gemini_response(input_text, image_path=None):
    model = genai.GenerativeModel('gemini-1.5-flash')
    inputs = [input_text]
    if image_path:
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
        image_parts = [{"mime_type": "image/jpeg", "data": image_data}]
        inputs.append(image_parts[0])
    
    response = model.generate_content(inputs, stream=True)
    response.resolve()
    return response.text

# Function to handle sending messages
def send_message():
    user_input = user_entry.get("1.0", tk.END).strip()
    if not user_input:
        messagebox.showwarning("Input Error", "Please enter a message.")
        return
    
    image_path = image_label.cget("text")
    chat_box.config(state=tk.NORMAL)
    chat_box.insert(tk.END, "You: " + user_input + "\n")
    if image_path:
        chat_box.insert(tk.END, "You uploaded an image.\n")
    
    chat_box.config(state=tk.DISABLED)
    user_entry.delete("1.0", tk.END)
    
    bot_response = get_gemini_response(user_input, image_path)
    chat_box.config(state=tk.NORMAL)
    chat_box.insert(tk.END, "Bot: " + bot_response + "\n")
    chat_box.config(state=tk.DISABLED)
    chat_box.yview(tk.END)
    
    image_label.config(text="")

# Function to handle image upload
def upload_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
    if file_path:
        image_label.config(text=file_path)

# Function to take screenshot
def take_screenshot():
    # Hide the Tkinter window
    root.withdraw()

    # Add a short delay to ensure the window is hidden before taking the screenshot
    time.sleep(0.2)

    # Take screenshot
    screenshot = pyautogui.screenshot()

    # Show the Tkinter window again
    root.deiconify()

    # Define the path for saving the screenshot
    temp_image_path = "temp_screenshot.jpg"
    screenshot.save(temp_image_path)

    # Display the screenshot in the Tkinter window
    display_screenshot(temp_image_path)

    # Show message box
    messagebox.showinfo("Screenshot Captured", f"Screenshot saved as {temp_image_path}")

# Function to display the screenshot
def display_screenshot(file_path):
    # Open the image file
    img = Image.open(file_path)
    
    # Resize the image to fit the label
    img = img.resize((1280, 720), Image.Resampling.LANCZOS)

    # Convert image to PhotoImage
    photo = ImageTk.PhotoImage(img)
    
    # Update the image label
    image_label.config(image=photo, text=file_path)
    image_label.image = photo  # Keep a reference to avoid garbage collection

# Main GUI setup
root = tk.Tk()
root.title("Gemini Chatbot")
root.geometry("400x600")
root.attributes("-topmost", True)  # Keep window on top

# Chat box
chat_box = scrolledtext.ScrolledText(root, state="disabled", wrap=tk.WORD)
chat_box.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

# User input entry
user_entry = tk.Text(root, height=3)
user_entry.pack(pady=5, padx=10, fill=tk.X)

# Image label to display uploaded image path or screenshot path
image_label = tk.Label(root, text="", bg="lightgray", anchor="w", relief="sunken")
image_label.pack(pady=5, padx=10, fill=tk.X)

# Upload image button
upload_button = tk.Button(root, text="Upload Image", command=upload_image)
upload_button.pack(pady=5)

# Take screenshot button
screenshot_button = tk.Button(root, text="Take Screenshot", command=take_screenshot)
screenshot_button.pack(pady=5)

# Send button
send_button = tk.Button(root, text="Send", command=send_message)
send_button.pack(pady=5)

root.mainloop()
