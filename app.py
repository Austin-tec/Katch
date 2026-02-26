import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)

# 1. ALLOW CROSS-ORIGIN REQUESTS
# This is the "bridge" that allows your Spck Editor site to talk to Railway.
CORS(app, resources={r"/*": {"origins": "*"}})

# 2. PREVIEW ROUTE
@app.route('/get_info', methods=['POST'])
def get_info():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"status": "error", "message": "No URL provided"}), 400
    
    url = data.get('url')
    ydl_opts = {'quiet': True, 'no_warnings': True}
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "status": "success",
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "video_url": info.get('url') # Direct stream link for the preview player
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 3. DOWNLOAD ROUTE
@app.route('/download', methods=['POST'])
def download_video():
    data = request.get_json()
    url = data.get('url')
    
    # Railway uses the /tmp folder for temporary file processing.
    # We use a static name here, or you could generate a random one.
    file_path = '/tmp/katch_video.mp4'

    # Clean up old file if it exists from a previous download
    if os.path.exists(file_path):
        os.remove(file_path)

    ydl_opts = {
        'format': 'best',
        'outtmpl': file_path,
        'restrictfilenames': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # 4. STREAM FILE TO BROWSER
        # Instead of saving to a phone folder, we send the bits directly to the user's browser.
        return send_file(
            file_path, 
            as_attachment=True, 
            download_name="katch_video.mp4",
            mimetype='video/mp4'
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 5. DYNAMIC PORT BINDING
if __name__ == '__main__':
    # Railway provides a 'PORT' environment variable. Your app MUST use it.
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
