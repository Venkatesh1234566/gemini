import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
from PIL import Image, ImageTk
import google.generativeai as genai
import pyautogui
import os
import time
import uuid

# Set the Google API Key
os.environ["GOOGLE_API_KEY"] = "AIzaSyDWzA4yiBc7amljOYTMnp8yxUgwB6YqGN4"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# List to keep track of uploaded and captured images
image_history = []

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
    
    chat_box.config(state=tk.NORMAL)
    
    # User message
    insert_message("You: " + user_input, "user")
    
    # Add some space between messages
    insert_message("\n", "space")
    
    # Bot response
    bot_response = get_gemini_response(user_input, image_history[-1] if image_history else None)
    insert_message("Bot: " + bot_response, "bot")
    chat_box.config(state=tk.DISABLED)
    chat_box.yview(tk.END)
    
    # Clear the image label
    image_label.config(text="")

# Function to insert message with rounded box
def insert_message(text, tag, image_path=None):
    chat_box.config(state=tk.NORMAL)
    
    if image_path:
        # Open the image file
        img = Image.open(image_path)
        # Resize the image to a small size
        img.thumbnail((500, 400), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        
        # Insert the image into the chat box
        chat_box.image_create(tk.END, image=photo)
        chat_box.insert(tk.END, "\n")
        chat_box.image = photo  # Keep a reference to avoid garbage collection
    
    # Insert the text
    chat_box.insert(tk.END, text + "\n", tag)
    
    # Configure the tag for background color
    chat_box.tag_configure(tag, background="azure3" if tag == "user" else "azure3", relief="flat")
    
    chat_box.config(state=tk.DISABLED)

# Function to handle image upload
def upload_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
    if file_path:
        # Save the image with a unique filename
        unique_filename = f"{uuid.uuid4().hex}.jpg"
        img = Image.open(file_path)
        img.save(os.path.join("saved_images", unique_filename))
        
        # Add to image history
        image_path = os.path.join("saved_images", unique_filename)
        image_history.append(image_path)
        
        # Display the uploaded image in the chatbox
        insert_message("Uploaded an image:", "user", image_path)

# Function to take screenshot
def take_screenshot():
    try:
        # Hide the Tkinter window
        root.withdraw()
        time.sleep(0.2)  # Short delay to ensure the window is hidden

        # Take screenshot
        screenshot = pyautogui.screenshot()

        # Define the path for saving the screenshot
        unique_filename = f"{uuid.uuid4().hex}.jpg"
        temp_image_path = os.path.join("saved_images", unique_filename)
        screenshot.save(temp_image_path)

        # Show the Tkinter window again
        root.deiconify()

        # Display the screenshot in the Tkinter window
        display_screenshot(temp_image_path)

        # Add to image history
        image_history.append(temp_image_path)

        # Show message box
        messagebox.showinfo("Screenshot Captured", f"Screenshot saved as {temp_image_path}")
        
        # Display the screenshot in the chatbox
        insert_message("Uploaded screenshot:", "user", temp_image_path)
    except Exception as e:
        root.deiconify()
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Function to display the screenshot
def display_screenshot(file_path):
    try:
        # Open the image file
        img = Image.open(file_path)
        
        # Resize the image to fit the label dynamically
        max_width = image_label.winfo_width()
        max_height = image_label.winfo_height()
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

        # Convert image to PhotoImage
        photo = ImageTk.PhotoImage(img)
        
        # Update the image label
        image_label.config(image=photo, text=file_path)
        image_label.image = photo  # Keep a reference to avoid garbage collection
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while displaying the screenshot: {str(e)}")

# Create a custom rounded rectangle on a Canvas
def draw_rounded_rectangle(canvas, x1, y1, x2, y2, radius, **kwargs):
    canvas.create_arc(x1, y1, x1 + 2*radius, y1 + 2*radius, start=90, extent=90, style=tk.ARC, **kwargs)
    canvas.create_arc(x2 - 2*radius, y1, x2, y1 + 2*radius, start=0, extent=90, style=tk.ARC, **kwargs)
    canvas.create_arc(x1, y2 - 2*radius, x1 + 2*radius, y2, start=180, extent=90, style=tk.ARC, **kwargs)
    canvas.create_arc(x2 - 2*radius, y2 - 2*radius, x2, y2, start=270, extent=90, style=tk.ARC, **kwargs)
    canvas.create_rectangle(x1 + radius, y1, x2 - radius, y2, **kwargs)
    canvas.create_rectangle(x1, y1 + radius, x2, y2 - radius, **kwargs)

# Main GUI setup
root = tk.Tk()
root.title("Gemini Chatbot")
root.geometry("500x900")
root.attributes("-topmost", True)  # Keep window on top

# Ensure the directory for saved images exists
if not os.path.exists("saved_images"):
    os.makedirs("saved_images")

# Chat box with Canvas for rounded corners
chat_frame = tk.Frame(root)
chat_frame.pack(pady=10, padx=10, fill=tk.BOTH)

chat_canvas = tk.Canvas(chat_frame, bg="black")
chat_canvas.pack(fill=tk.BOTH, expand=True)

chat_box = tk.Text(chat_canvas, wrap=tk.WORD, bg="black", font=("Arial", 12),height=23)
chat_box.pack(pady=0, padx=0, fill=tk.BOTH, expand=True)

# Configure tags for user and bot messages
chat_box.tag_configure("user", background="azure3", relief="flat")  # Light grey for user
chat_box.tag_configure("bot", background="lightgreen", relief="flat")  # Light green for bot
chat_box.tag_configure("space", background="black")  # Background for space between messages

# User input entry with placeholder
user_entry = tk.Text(root, height=3, wrap=tk.WORD)
user_entry.pack(pady=5, padx=10, fill=tk.X)
user_entry.insert("1.0", "Type your message here...", "placeholder")

# Image label to display uploaded image path or screenshot path
image_label = tk.Label(root, text="", bg="lightgray", anchor="w", relief="sunken")
image_label.pack(pady=5, padx=10, fill=tk.X)

# Frame for buttons to align them vertically and center them
button_frame = tk.Frame(root)
button_frame.pack(pady=5, padx=10, fill=tk.X)

# Send button
send_button = tk.Button(button_frame, text="Send Text", command=send_message, bg="black", fg="white")
send_button.pack(pady=5, side=tk.TOP, anchor="center")

# Frame for the upload and screenshot buttons
image_button_frame = tk.Frame(button_frame)
image_button_frame.pack(pady=5, fill=tk.X)

# Upload image button
upload_button = tk.Button(image_button_frame, text="Upload Image", command=upload_image, bg="aquamarine3")
upload_button.pack(pady=5, side=tk.LEFT, expand=True, fill=tk.X)

# Take screenshot button
screenshot_button = tk.Button(image_button_frame, text="Take Screenshot", command=take_screenshot, bg="dodgerblue4", fg="white")
screenshot_button.pack(pady=5, side=tk.RIGHT, expand=True, fill=tk.X)

root.mainloop()
