Katch 🎬
Katch is a lightweight, self-hosted video downloader API built with Python and Flask. It accepts a video URL (YouTube and other supported platforms), fetches video metadata for preview, and streams the downloaded video file directly to the user's browser — no file storage required on the client side.
It is designed to be deployed on platforms like Railway and consumed by any frontend (including Spck Editor-hosted static sites) via simple HTTP requests.
Table of Contents
Features
Tech Stack
Project Structure
How It Works
API Reference
Local Development Setup
Deployment (Railway)
Environment Variables
Frontend Integration
Known Limitations
Features
🔍 Preview before download — Fetch video title and thumbnail from any supported URL before committing to a download.
⬇️ Stream to browser — Video is downloaded on the server and streamed directly to the user as a .mp4 file attachment.
🌐 CORS-enabled — Configured to accept requests from any origin, making it easy to connect any frontend.
🚀 Railway-ready — Includes a Procfile for one-click deployment on Railway's platform.
🧹 Automatic cleanup — Old temporary files are deleted before each new download to prevent disk bloat.
Tech Stack
Layer
Technology
Language
Python 3
Web Framework
Flask
CORS
Flask-CORS
Video Engine
yt-dlp
WSGI Server
Gunicorn (for production)
Deployment
Railway
Project Structure
Katch-main/
├── app.py              # Main Flask application — all routes and logic
├── Procfile            # Tells Railway/Heroku how to start the server
└── requirements.txt    # Python dependencies
File Breakdown
app.py
The entire backend lives here. It exposes two POST endpoints:
/get_info — Extracts video metadata without downloading.
/download — Downloads the video to /tmp and streams it to the client.
Procfile
web: gunicorn app:app
This tells the deployment platform to start the app using Gunicorn (a production-grade WSGI server) instead of Flask's built-in development server.
requirements.txt
flask
flask-cors
yt-dlp
gunicorn
All four packages are required for the app to run in production.
How It Works
Client (Browser/Frontend)
        |
        |  POST /get_info  { "url": "https://youtube.com/watch?v=..." }
        ↓
   Flask API (Railway)
        |
        |  yt-dlp extracts title, thumbnail, direct stream URL
        ↓
   JSON response → Frontend shows preview
        |
        |  POST /download  { "url": "https://youtube.com/watch?v=..." }
        ↓
   Flask API downloads video → saves to /tmp/katch_video.mp4
        |
        |  send_file() streams the .mp4 back to the browser
        ↓
   Browser triggers native download prompt
The frontend sends a video URL to /get_info.
yt-dlp fetches the metadata (no download happens).
The frontend displays the title and thumbnail for confirmation.
The user initiates the download — the frontend sends the URL to /download.
The server uses yt-dlp to download the best available quality to /tmp/katch_video.mp4.
Flask streams the file to the browser using send_file() with as_attachment=True, triggering the browser's native file download.
API Reference
POST /get_info
Fetches video metadata without downloading.
Request Body:
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
Success Response (200):
{
  "status": "success",
  "title": "Rick Astley - Never Gonna Give You Up",
  "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
  "video_url": "https://..."
}
Error Response (400 / 500):
{
  "status": "error",
  "message": "No URL provided"
}
POST /download
Downloads the video and streams it to the client as a .mp4 file.
Request Body:
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
Success Response (200):
Binary stream with headers:
Content-Disposition: attachment; filename="katch_video.mp4"
Content-Type: video/mp4
Error Response (500):
{
  "status": "error",
  "message": "<yt-dlp error message>"
}
Local Development Setup
Prerequisites
Python 3.8 or higher
pip (Python package manager)
ffmpeg installed on your system (recommended for yt-dlp to merge formats)
Steps
1. Clone or extract the project
# If using git:
git clone https://github.com/your-username/Katch.git
cd Katch

# Or extract the zip and navigate into it:
cd Katch-main
2. Create and activate a virtual environment (recommended)
# Create virtual environment
python -m venv venv

# Activate on Linux/macOS:
source venv/bin/activate

# Activate on Windows (PowerShell):
venv\Scripts\Activate.ps1
3. Install dependencies
pip install -r requirements.txt
4. Run the development server
python app.py
The server starts at: http://localhost:5000
5. Test the API
Using curl:
# Test /get_info
curl -X POST http://localhost:5000/get_info \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'

# Test /download (saves output to file)
curl -X POST http://localhost:5000/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}' \
  --output video.mp4
Or using a REST client like Postman or Thunder Client (VS Code extension).
Deployment (Railway)
One-Time Setup
Create a Railway account at railway.app
Create a new project and choose "Deploy from GitHub repo" (or use the Railway CLI)
Connect your repository containing the Katch source files
Railway will auto-detect the Procfile and deploy using Gunicorn
Automatic Configuration
Railway automatically provides a PORT environment variable. The app is already configured to use it:
port = int(os.environ.get("PORT", 5000))
app.run(host='0.0.0.0', port=port)
You do not need to set this manually.
After Deployment
Railway will give you a public URL like:
https://katch-production.up.railway.app
Use this as the base URL for all API calls from your frontend.
Environment Variables
Variable
Required
Default
Description
PORT
Yes (auto-set by Railway)
5000
The port the server listens on
No other environment variables are required for basic operation.
Frontend Integration
Katch is built to be called from any JavaScript frontend. Here's a minimal example:
const API_BASE = "https://your-katch-app.up.railway.app";

// Step 1: Preview
async function previewVideo(url) {
  const response = await fetch(`${API_BASE}/get_info`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url })
  });
  const data = await response.json();
  if (data.status === "success") {
    console.log("Title:", data.title);
    console.log("Thumbnail:", data.thumbnail);
  }
}

// Step 2: Download
async function downloadVideo(url) {
  const response = await fetch(`${API_BASE}/download`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url })
  });

  // Create a blob from the binary stream and trigger download
  const blob = await response.blob();
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "katch_video.mp4";
  link.click();
}
