# 🌌 Planetary Mission Explorer

A modern, interactive web application that allows users to explore NASA's vast collection of space data, including Earth satellite imagery and Mars rover photographs.

## 🚀 Features

- **🌍 Earth Imagery**: Get high-resolution satellite images from any location on Earth
- **🔄 Image Comparison**: Compare changes over time with side-by-side image analysis
- **🔴 Mars Rover Photos**: Explore thousands of images from NASA's Mars rovers
- **🎨 Modern UI**: Beautiful, responsive design with smooth animations
- **📱 Mobile Friendly**: Optimized for all device sizes

## 🛠️ Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **APIs**: NASA Earth Assets API, NASA Mars Rover Photos API
- **Styling**: Modern CSS with CSS Grid, Flexbox, and CSS Variables
- **Deployment**: Railway/Heroku ready

## 📋 Prerequisites

- Python 3.8 or higher
- NASA API Key (free from [api.nasa.gov](https://api.nasa.gov/#signUp))

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/planetary-mission-explorer.git
   cd planetary-mission-explorer
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Get your NASA API Key**
   - Visit [api.nasa.gov](https://api.nasa.gov/#signUp)
   - Sign up for a free account
   - Copy your API key

5. **Update the API key in app.py**
   ```python
   API_KEY = "your-nasa-api-key-here"
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Open your browser**
   Navigate to `http://localhost:5000`

## 🌐 Live Deployment

### Option 1: Railway (Recommended)

1. **Fork this repository** to your GitHub account
2. **Sign up** at [railway.app](https://railway.app)
3. **Connect your GitHub** account
4. **Create a new project** and select "Deploy from GitHub repo"
5. **Select your forked repository**
6. **Add environment variables**:
   - `NASA_API_KEY`: Your NASA API key
7. **Deploy** and get your live URL!

### Option 2: Heroku

1. **Install Heroku CLI**
2. **Login to Heroku**
   ```bash
   heroku login
   ```
3. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```
4. **Set environment variables**
   ```bash
   heroku config:set NASA_API_KEY=your-api-key-here
   ```
5. **Deploy**
   ```bash
   git push heroku main
   ```

### Option 3: Render

1. **Sign up** at [render.com](https://render.com)
2. **Connect your GitHub** repository
3. **Create a new Web Service**
4. **Configure**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. **Add environment variables**:
   - `NASA_API_KEY`: Your NASA API key
6. **Deploy**

## 📁 Project Structure

```
planetary-mission-explorer/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Procfile              # Deployment configuration
├── runtime.txt           # Python version
├── .gitignore           # Git ignore rules
├── README.md            # This file
├── static/
│   └── style.css        # Modern CSS styles
└── templates/
    ├── index.html       # Home page
    ├── earth.html       # Earth imagery page
    └── mars.html        # Mars rover page
```

## 🔑 API Configuration

The application uses two main NASA APIs:

1. **Earth Assets API**: For satellite imagery
   - Endpoint: `https://api.nasa.gov/planetary/earth/assets`
   - Parameters: lat, lon, date, dim, api_key

2. **Mars Rover Photos API**: For Mars rover images
   - Endpoint: `https://api.nasa.gov/mars-photos/api/v1/rovers/{rover}/photos`
   - Parameters: sol, camera, api_key

## 🎨 Customization

### Colors and Themes
The application uses CSS custom properties for easy theming. Edit `static/style.css`:

```css
:root {
    --accent-primary: #64FFDA;    /* Main accent color */
    --bg-primary: #0A0A0F;        /* Background color */
    --text-primary: #FFFFFF;      /* Text color */
}
```

### Adding New Features
1. **New API endpoints**: Add routes in `app.py`
2. **New pages**: Create templates in `templates/`
3. **Styling**: Update `static/style.css`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [NASA Open APIs](https://api.nasa.gov/) for providing free access to space data
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Inter Font](https://rsms.me/inter/) for beautiful typography

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/planetary-mission-explorer/issues) page
2. Create a new issue with detailed information
3. Include your Python version and error messages

---

**Made with ❤️ for space exploration enthusiasts** 