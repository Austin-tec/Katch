from flask import Flask, request, jsonify
from flask_cors import CORS # This is the bridge to Spck Editor
import yt_dlp

app = Flask(__name__)
CORS(app) # Allows the frontend connection

# The universal Android download path
SAVE_PATH = '/sdcard/Download/%(title)s.%(ext)s'

# --- 1. PREVIEW ROUTE ---
@app.route('/get_info', methods=['POST'])
def get_info():
    data = request.get_json()
    url = data.get('url')
    
    # We use download=False to just 'scout' the video info quickly
    ydl_opts = {'quiet': True, 'no_warnings': True}
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "status": "success",
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "video_url": info.get('url') # Direct link for your player
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- 2. DOWNLOAD ROUTE ---
@app.route('/download', methods=['POST'])
def download_video():
    data = request.get_json()
    url = data.get('url')

    ydl_opts = {
        'format': 'best',
        'outtmpl': SAVE_PATH,
        'restrictfilenames': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return jsonify({"status": "success", "message": "Saved to Downloads!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
