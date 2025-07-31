from flask import Flask, request, render_template, url_for, Response
import requests
import os
import uuid # To generate unique filenames
from PIL import Image, ImageEnhance, ImageFilter # For image enhancement

app = Flask(__name__)

# Ensure the static directory exists for saving images
if not os.path.exists(app.static_folder):
    os.makedirs(app.static_folder)

# --- IMPORTANT: Replace with your actual NASA API Key ---
API_KEY = "vxNXyxn7JteE6pLjj7dqmgfXuQR2hqDeHlVVUHGD"
# For production, consider using environment variables for API keys
# e.g., API_KEY = os.environ.get("NASA_API_KEY")
# --------------------------------------------------------

# --- NEW: Helper function to fetch, enhance, and save a single image ---
# Returns (image_url, filepath, PIL_Image_object) or (None, None, None) on failure
def process_nasa_image(lat, lon, date, dim, api_key, brightness_factor, contrast_factor, saturation_factor, sharpness_factor, warmth_red_factor, warmth_green_factor, warmth_blue_factor, filename_prefix):
    try:
        base_url = "https://api.nasa.gov/planetary/earth/assets"
        params = {
            "lat": lat,
            "lon": lon,
            "date": date,
            "dim": dim,
            "api_key": api_key,
        }

        res = requests.get(base_url, params=params)
        res.raise_for_status()
        data = res.json()

        if "url" in data and data["url"]:
            img_url = data["url"]
            img_response = requests.get(img_url)
            img_response.raise_for_status()

            content_type = img_response.headers.get('Content-Type', '').lower()
            file_extension = 'jpeg'
            if 'jpeg' in content_type or 'jpg' in content_type:
                file_extension = 'jpeg'
            elif 'png' in content_type:
                file_extension = 'png'

            unique_filename = f"{filename_prefix}_{uuid.uuid4()}.{file_extension}"
            filepath = os.path.join(app.static_folder, unique_filename)

            with open(filepath, "wb") as f:
                f.write(img_response.content)

            img = Image.open(filepath)

            # Apply enhancements
            if img.mode != 'RGB':
                img = img.convert('RGB')

            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(brightness_factor)

            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(contrast_factor)

            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(saturation_factor)

            r, g, b = img.split()
            enhancer_r = ImageEnhance.Brightness(r)
            r = enhancer_r.enhance(warmth_red_factor)
            enhancer_g = ImageEnhance.Brightness(g)
            g = enhancer_g.enhance(warmth_green_factor)
            enhancer_b = ImageEnhance.Brightness(b)
            b = enhancer_b.enhance(warmth_blue_factor)
            img = Image.merge('RGB', (r, g, b))

            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(sharpness_factor)
            img = img.filter(ImageFilter.DETAIL)

            img.save(filepath) # Overwrite with enhanced version
            return url_for('static', filename=unique_filename), filepath, img # Return URL, filepath, and enhanced PIL Image object
        else:
            return None, None, None # No image URL found

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response else "Unknown"
        print(f"NASA API Error processing {filename_prefix}: {status_code} - {e}")
        return None, None, None
    except requests.exceptions.ConnectionError:
        print(f"Network connection error processing {filename_prefix}.")
        return None, None, None
    except Exception as e:
        print(f"An unexpected error occurred processing {filename_prefix}: {e}")
        return None, None, None

# --- NEW: Helper function to fetch Mars rover images ---
def fetch_mars_rover_images(rover, sol, camera, api_key):
    """
    Fetch Mars rover images using NASA's Mars Rover Photos API.
    
    Args:
        rover (str): Rover name (curiosity, opportunity, spirit)
        sol (int): Martian day (sol)
        camera (str): Camera name (optional)
        api_key (str): NASA API key
    
    Returns:
        dict: API response with image data
    """
    try:
        base_url = "https://api.nasa.gov/mars-photos/api/v1/rovers"
        url = f"{base_url}/{rover}/photos"
        
        params = {
            "sol": sol,
            "api_key": api_key
        }
        
        if camera and camera != "all":
            params["camera"] = camera
            
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.HTTPError as e:
        print(f"NASA Mars API Error: {e}")
        return {"error": f"API Error: {e}"}
    except requests.exceptions.ConnectionError:
        print("Network connection error fetching Mars images.")
        return {"error": "Network connection error"}
    except Exception as e:
        print(f"Unexpected error fetching Mars images: {e}")
        return {"error": f"Unexpected error: {e}"}

# --- NEW: Helper function to get available Mars rovers ---
def get_mars_rovers(api_key):
    """
    Get list of available Mars rovers.
    
    Args:
        api_key (str): NASA API key
    
    Returns:
        dict: API response with rover data
    """
    try:
        url = "https://api.nasa.gov/mars-photos/api/v1/rovers"
        params = {"api_key": api_key}
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.HTTPError as e:
        print(f"NASA Mars API Error: {e}")
        return {"error": f"API Error: {e}"}
    except requests.exceptions.ConnectionError:
        print("Network connection error fetching Mars rovers.")
        return {"error": "Network connection error"}
    except Exception as e:
        print(f"Unexpected error fetching Mars rovers: {e}")
        return {"error": f"Unexpected error: {e}"}

@app.route("/")
def index():
    """
    Renders the main index page of the Planetary Mission Explorer.
    This is the first page users will see.
    """
    return render_template("index.html")

@app.route("/earth", methods=["GET", "POST"])
def earth():
    """
    Handles requests for the Earth imagery page.
    - GET: Displays the form to request Earth images.
    - POST: Processes the form data, fetches an image from NASA,
            saves it locally, and displays it on the page.
    """
    # --- Existing Variables for the "Get Single/Dual Images" form and display ---
    image_display_url = None
    image_display_url_2 = None
    error_message = None # This will now be specific to the single/dual form
    api_val = ""
    lat_val = ""
    lon_val = ""
    date_val = ""
    date2_val = ""
    area_val = ""

    # --- NEW: Variables for the "Compare & Collage Images" form and display ---
    collaged_image_url = None # URL for the collaged image
    error_collage = None # Error message specific to the collage section

    api_collage_val = "" # Persistence for collage form
    latitude_collage_val = ""
    longitude_collage_val = ""
    date1_collage_val = ""
    date2_collage_val = ""
    area_collage_val = ""

    # --- Enhancement factors (common for both forms, adjust as needed) ---
    brightness_factor = 2
    contrast_factor = 2.2
    saturation_factor = 3
    sharpness_factor = 2
    warmth_red_factor = 1.5
    warmth_green_factor = 1.5
    warmth_blue_factor = 0.8

    if request.method == "POST":
        # NEW: Determine which form was submitted using the hidden input 'form_type'
        form_type = request.form.get("form_type")

        # --- Logic for "Get Single/Dual Images" form ---
        if form_type == "single_dual":
            # Get form data for first image (existing variables)
            api = request.form.get("api")
            lat = request.form.get("latitude")
            lon = request.form.get("longitude")
            date = request.form.get("date")
            area = request.form.get("area")
            date2 = request.form.get("date2") # Optional second date for this form

            # Store values for re-populating the form
            api_val = api if api else ""
            lat_val = lat if lat else ""
            lon_val = lon if lon else ""
            date_val = date if date else ""
            date2_val = date2 if date2 else ""
            area_val = area if area else ""

            # Basic validation for required fields
            if not all([api, lat, lon, date, area]):
                error_message = "Please provide API Key, Latitude, Longitude, Date 1, and Area for separate images."
            else:
                try:
                    float(lat)
                    float(lon)
                except ValueError:
                    error_message = "Latitude and Longitude must be valid numbers."

            dim = None
            area_int = None
            if not error_message:
                try:
                    area_int = int(area)
                    if area_int <= 0:
                        error_message = "Image area must be a positive integer."
                except ValueError:
                    error_message = "Invalid image area selected. Please choose from the provided options."

            if not error_message: # Proceed only if no validation errors
                if area_int == 1: dim = 0.009
                elif area_int == 25: dim = 0.045
                elif area_int == 100: dim = 0.090
                elif area_int == 400: dim = 0.180
                elif area_int == 2500: dim = 0.450
                elif area_int == 10000: dim = 0.901
                else: error_message = "Invalid image area selected. Please choose from the provided options."

            # Process First Image (Date 1)
            if not error_message and dim is not None:
                # Call helper function to process the first image
                url1, _, _ = process_nasa_image(lat, lon, date, dim, api,
                                                brightness_factor, contrast_factor, saturation_factor,
                                                sharpness_factor, warmth_red_factor, warmth_green_factor, warmth_blue_factor,
                                                "earth_image_date1")

                if url1:
                    image_display_url = url1
                else:
                    error_message = "No image found for Date 1. Try different coordinates or a date with known imagery (e.g., San Francisco: 37.77, -122.41, 2023-01-15)."

                # Process Second Image (Date 2) if provided
                if not error_message and date2: # Only try to get date2 if date1 was fine or initial error wasn't critical
                    url2, _, _ = process_nasa_image(lat, lon, date2, dim, api,
                                                    brightness_factor, contrast_factor, saturation_factor,
                                                    sharpness_factor, warmth_red_factor, warmth_green_factor, warmth_blue_factor,
                                                    "earth_image_date2")
                    if url2:
                        image_display_url_2 = url2
                    else:
                        if not error_message: # Only set this error if no prior error exists
                            error_message = "No image found for Date 2. Try a different date."
                
                # If neither image could be fetched and no specific error was set, provide a general one.
                if not image_display_url and not image_display_url_2 and not error_message:
                    error_message = "Could not retrieve any images for the given parameters. Please check your API Key and input."

        # --- NEW: Logic for "Compare & Collage Images" form ---
        elif form_type == "collage":
            # Get form data for collage (new variables)
            api_collage = request.form.get("api_collage")
            latitude_collage = request.form.get("latitude_collage")
            longitude_collage = request.form.get("longitude_collage")
            date1_collage = request.form.get("date1_collage")
            date2_collage = request.form.get("date2_collage")
            area_collage = request.form.get("area_collage")

            # Store values for re-populating the collage form
            api_collage_val = api_collage if api_collage else ""
            latitude_collage_val = latitude_collage if latitude_collage else ""
            longitude_collage_val = longitude_collage if longitude_collage else ""
            date1_collage_val = date1_collage if date1_collage else ""
            date2_collage_val = date2_collage if date2_collage else ""
            area_collage_val = area_collage if area_collage else ""

            # Validation for collage form (both dates are required here)
            if not all([api_collage, latitude_collage, longitude_collage, date1_collage, date2_collage, area_collage]):
                error_collage = "Please provide API Key, Latitude, Longitude, BOTH Dates, and Area for collage."
            else:
                try:
                    float(latitude_collage)
                    float(longitude_collage)
                except ValueError:
                    error_collage = "Latitude and Longitude must be valid numbers."

            dim_collage = None
            area_collage_int = None
            if not error_collage:
                try:
                    area_collage_int = int(area_collage)
                    if area_collage_int <= 0:
                        error_collage = "Image area must be a positive integer."
                except ValueError:
                    error_collage = "Invalid image area selected. Please choose from the provided options."

            if not error_collage: # Proceed only if no validation errors
                if area_collage_int == 1: dim_collage = 0.009
                elif area_collage_int == 25: dim_collage = 0.045
                elif area_collage_int == 100: dim_collage = 0.090
                elif area_collage_int == 400: dim_collage = 0.180
                elif area_collage_int == 2500: dim_collage = 0.450
                elif area_collage_int == 10000: dim_collage = 0.901
                else: error_collage = "Invalid image area selected. Please choose from the provided options."

            # Process both images for collage if no errors and dim is set
            if not error_collage and dim_collage is not None:
                # Get the first image
                url1_collage, filepath1_collage, pil_img1 = process_nasa_image(
                    latitude_collage, longitude_collage, date1_collage, dim_collage, api_collage,
                    brightness_factor, contrast_factor, saturation_factor,
                    sharpness_factor, warmth_red_factor, warmth_green_factor, warmth_blue_factor,
                    "earth_collage_date1"
                )

                # Get the second image
                url2_collage, filepath2_collage, pil_img2 = process_nasa_image(
                    latitude_collage, longitude_collage, date2_collage, dim_collage, api_collage,
                    brightness_factor, contrast_factor, saturation_factor,
                    sharpness_factor, warmth_red_factor, warmth_green_factor, warmth_blue_factor,
                    "earth_collage_date2"
                )

                if pil_img1 and pil_img2:
                    try:
                    
                        if pil_img1.size != pil_img2.size:
                            max_width = max(pil_img1.width, pil_img2.width)
                            max_height = max(pil_img1.height, pil_img2.height)
                            pil_img1 = pil_img1.resize((max_width, max_height))
                            pil_img2 = pil_img2.resize((max_width, max_height))

                        # Create a new image for the collage
                        total_width = pil_img1.width + pil_img2.width
                        max_height = max(pil_img1.height, pil_img2.height) # Should be same after resize

                        collaged_img = Image.new('RGB', (total_width, max_height))
                        collaged_img.paste(pil_img1, (0, 0))
                        collaged_img.paste(pil_img2, (pil_img1.width, 0))

                        # Save the collaged image
                        collage_filename = f"earth_collage_{date1_collage}_{date2_collage}_{uuid.uuid4()}.jpeg"
                        collage_filepath = os.path.join(app.static_folder, collage_filename)
                        collaged_img.save(collage_filepath, "jpeg")
                        collaged_image_url = url_for('static', filename=collage_filename)

                    except Exception as e:
                        error_collage = f"Failed to create collage image: {e}"
                        print(f"Error creating collage: {e}")
                else:
                    error_collage = "Could not retrieve both images for collage. Ensure imagery is available for both dates."

    # Render the earth.html template, passing all relevant variables for both sections
    return render_template("earth.html",
                           # Variables for Single/Dual Images section
                           error_single_dual=error_message, # Renamed to be specific
                           image_url=image_display_url,
                           image_url_2=image_display_url_2,
                           api_val=api_val,
                           latitude=lat_val,
                           longitude=lon_val,
                           date_val=date_val,
                           date2_val=date2_val,
                           area_val=area_val,

                           # NEW Variables for Compare & Collage Images section
                           error_collage=error_collage,
                           collaged_image_url=collaged_image_url,
                           api_collage_val=api_collage_val,
                           latitude_collage_val=latitude_collage_val,
                           longitude_collage_val=longitude_collage_val,
                           date1_collage_val=date1_collage_val,
                           date2_collage_val=date2_collage_val,
                           area_collage_val=area_collage_val
                           )

@app.route("/mars", methods=["GET", "POST"])
def mars():
    """
    Renders the Mars exploration page and handles Mars rover image requests.
    """
    message = "Welcome to Mars! Explore rover images from the Red Planet."
    images = []
    rovers_data = []
    selected_rover = "curiosity"
    selected_sol = 1000
    selected_camera = "all"
    
    if request.method == "POST":
        selected_rover = request.form.get("rover", "curiosity")
        selected_sol = int(request.form.get("sol", 1000))
        selected_camera = request.form.get("camera", "all")
        
        # Fetch Mars rover images
        mars_data = fetch_mars_rover_images(selected_rover, selected_sol, selected_camera, API_KEY)
        
        if "error" not in mars_data and "photos" in mars_data:
            images = mars_data["photos"]
            message = f"Found {len(images)} images from {selected_rover.title()} on sol {selected_sol}"
            if selected_camera != "all":
                message += f" using {selected_camera.upper()} camera"
        else:
            message = f"Error fetching Mars images: {mars_data.get('error', 'Unknown error')}"
    
    # Get available rovers
    rovers_response = get_mars_rovers(API_KEY)
    if "error" not in rovers_response and "rovers" in rovers_response:
        rovers_data = rovers_response["rovers"]
    
    return render_template("mars.html", 
                         message=message, 
                         images=images, 
                         rovers=rovers_data,
                         selected_rover=selected_rover,
                         selected_sol=selected_sol,
                         selected_camera=selected_camera)

if __name__ == "__main__":
    app.run(debug=True)
