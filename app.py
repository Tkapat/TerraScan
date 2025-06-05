from flask import Flask, request, render_template, url_for, Response
import requests
import os
import uuid # To generate unique filenames

app = Flask(__name__)

# Ensure the static directory exists for saving images
# app.static_folder points to 'static' by default
if not os.path.exists(app.static_folder):
    os.makedirs(app.static_folder)

# --- IMPORTANT: Replace with your actual NASA API Key ---
API_KEY = "vxNXyxn7JteE6pLjj7dqmgfXuQR2hqDeHlVVUHGD"
# For production, consider using environment variables for API keys
# e.g., API_KEY = os.environ.get("NASA_API_KEY")
# --------------------------------------------------------

# --- NEW: Route for the central landing page (index.html) ---
# This function will be called when someone visits the base URL, e.g., http://127.0.0.1:5000/
@app.route("/")
def index():
    """
    Renders the main index page of the Planetary Mission Explorer.
    This is the first page users will see.
    """
    return render_template("index.html")

# --- Existing: Route for the Earth page (earth.html) ---
# This function handles displaying the Earth imagery form and processing submissions.
@app.route("/earth", methods=["GET", "POST"])
def earth():
    """
    Handles requests for the Earth imagery page.
    - GET: Displays the form to request Earth images.
    - POST: Processes the form data, fetches an image from NASA,
            saves it locally, and displays it on the page.
    """
    image_display_url = None
    error_message = None
    api_val=""
    lat_val = ""
    lon_val = ""
    date_val = ""
    area_val= ""

    if request.method == "POST":
        api=request.form.get("api")
        lat = request.form.get("latitude")
        lon = request.form.get("longitude")
        date = request.form.get("date")
        area= request.form.get("area") # Image size for NASA Earth imagery API

        api_val= api if api else ""
        lat_val = lat if lat else ""
        lon_val = lon if lon else ""
        date_val = date if date else ""
        area_val= area if area else ""

        # Basic validation: Check if all fields are provided
        if not all([api,lat, lon, date,area]):
            error_message = "Please provide latitude, longitude, and date for the image."
        else:
            # Basic validation: Check if latitude and longitude are valid numbers
            try:
                float(lat)
                float(lon)
            except ValueError:
                error_message = "Latitude and Longitude must be valid numbers."
        area_int = None
        if not error_message:
            try:
                area_int = int(area) # <--- CRITICAL: Convert to integer here
                if area_int <= 0:
                    error_message = "Image area must be a positive integer."
            except ValueError:
                error_message = "Invalid image area selected. Please choose from the provided options."
        dim=None
        if not error_message: # Proceed only if no validation errors
            if area_int == 1:
                dim = 0.009
            elif area_int == 25:
                dim = 0.045
            elif area_int == 100: # Added 10Km X 10Km
                dim = 0.090
            elif area_int == 400:
                dim = 0.180
            elif area_int == 2500:
                dim = 0.450
            elif area_int == 10000:
                dim = 0.901
            else:
                # If 'area' doesn't match any known options, set an error
                error_message = "Invalid image area selected. Please choose from the provided options."
        if not error_message and dim is not None:
            url = "https://api.nasa.gov/planetary/earth/assets"
            params = {
                "lat": lat,
                "lon": lon,
                "date": date,
                "dim": dim,
                "api_key": api,
            }

            try:
                # 1. Get metadata (which includes the actual image URL) from NASA
                res = requests.get(url, params=params)
                res.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
                data = res.json()

                if "url" in data and data["url"]: # Ensure 'url' exists and is not empty
                    img_url = data["url"]
                    # 2. Download the actual image content from the URL provided by NASA
                    img_response = requests.get(img_url)
                    img_response.raise_for_status() # Raise for errors on image fetch

                    # Determine image extension based on Content-Type header (simple heuristic)
                    content_type = img_response.headers.get('Content-Type', '').lower()
                    if 'jpeg' in content_type or 'jpg' in content_type:
                        file_extension = 'jpeg'
                    elif 'png' in content_type:
                        file_extension = 'png'
                    else:
                        # Default to jpeg if type is unknown or not common
                        file_extension = 'jpeg'

                    # Generate a unique filename to avoid conflicts
                    unique_filename = f"earth_image_{uuid.uuid4()}.{file_extension}"
                    # Construct the full path to save the image in the static folder
                    filepath = os.path.join(app.static_folder, unique_filename)

                    # 3. Save the image to the static folder on your server
                    with open(filepath, "wb") as f:
                        f.write(img_response.content)

                    # 4. Generate a URL that the HTML template can use to link to the locally saved image
                    image_display_url = url_for('static', filename=unique_filename)

                else:
                    error_message = "No image found for the specified location and date. Try different coordinates or a date with known imagery (e.g., San Francisco: 37.77, -122.41, 2023-01-15)."

            except requests.exceptions.HTTPError as e:
                # Handle specific HTTP errors from NASA API (e.g., 400 Bad Request, 404 Not Found)
                status_code = e.response.status_code if e.response else "Unknown"
                error_message = f"NASA API Error: {status_code}. " \
                                f"Please check your coordinates and date. " \
                                "Often, no imagery exists for specific points or dates or the API key is invalid."
            except requests.exceptions.ConnectionError:
                # Handle network connection issues
                error_message = "Network connection error. Please check your internet connection."
            except Exception as e:
                # Catch any other unexpected errors during the process
                error_message = f"An unexpected error occurred: {e}"

    # Render the earth.html template, passing any messages and the image URL
    return render_template("earth.html",
                           error=error_message,
                           image_url=image_display_url,
                           latitude=lat_val,
                           longitude=lon_val,
                           date=date_val)

# --- NEW: Route for the Mars page (mars.html) ---
# This function will be called when someone visits /mars, e.g., http://127.0.0.1:5000/mars
@app.route("/mars")
def mars():
    """
    Renders the Mars exploration page.
    You would add Mars-specific backend logic (e.g., API calls for Mars rovers) here.
    """
    # For now, it just renders the mars.html template with a simple message.
    return render_template("mars.html", message="Welcome to Mars! More data coming soon...")

if __name__ == "__main__":
    # Run the Flask development server.
    # debug=True enables auto-reloading on code changes and a debugger.
    app.run(debug=True)
