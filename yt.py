import yt_dlp
import os
import threading
import time
from flask import Flask, request, send_file, render_template_string
from colorama import init, Fore

# Initialize colorama for cross-platform color support
init(autoreset=True)

app = Flask(__name__)

# Define the dynamic path to save the video in the same directory as the script
download_path = os.path.dirname(os.path.abspath(__file__))

# Function to display progress in a single line
def progress_hook(d):
    if d['status'] == 'finished':
        print(f"{Fore.CYAN}✔ {Fore.GREEN}Download completed successfully!")

# Function to download YouTube video
def download_video(url):
    ydl_opts = {
        'format': 'best',
        'progress_hooks': [progress_hook],
        'quiet': True,
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url)
        file_path = ydl.prepare_filename(info)
    return file_path

# Function to delete the file after a given delay
def delete_file_after_delay(file_path, delay):
    time.sleep(delay)
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"{Fore.RED}Deleted file: {file_path}")

# Route to serve the download page
@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Video Downloader</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/css/bootstrap.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Poppins', sans-serif;
            background-color: #121212;
            color: #FFFFFF;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 0;
            transition: background-color 0.3s ease;
        }

        .container {
            background-color: #1E1E1E;
            border-radius: 15px;
            padding: 40px;
            max-width: 500px;
            width: 100%;
            box-shadow: 0px 15px 25px rgba(0, 0, 0, 0.5);
            animation: fadeInUp 1s ease-in-out;
            text-align: center;
            position: relative;
        }

        h1 {
            color: #FF9800;
            font-weight: 600;
            margin-bottom: 20px;
            font-size: 2.2rem;
        }

        label {
            font-size: 1rem;
            margin-bottom: 10px;
            color: #FFF;
        }

        input[type="text"] {
            width: 100%;
            padding: 10px;
            margin: 15px 0;
            border: 1px solid #444;
            border-radius: 5px;
            background-color: #2C2C2C;
            color: #FFF;
            font-size: 1rem;
        }

        input[type="submit"] {
            background-color: #FF9800;
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            width: 100%;
            font-size: 1.2rem;
            transition: background-color 0.3s ease;
        }

        input[type="submit"]:hover {
            background-color: #FF5722;
        }

        .loading {
            display: none;
            margin-top: 20px;
        }

        .dark-mode-toggle {
            position: absolute;
            top: 20px;
            right: 20px;
            cursor: pointer;
            font-size: 1.5rem;
            color: #FF9800;
            transition: color 0.3s ease;
        }

        .dark-mode-toggle:hover {
            color: #FF5722;
        }

        footer {
            margin-top: 20px;
            font-size: 0.85rem;
            color: #777;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    </style>
</head>
<body>

    <div class="dark-mode-toggle" onclick="toggleDarkMode()">🌙</div>

    <div class="container">
        <h1><i class="fas fa-download"></i> YouTube Video Downloader</h1>
        <form action="/download" method="POST" onsubmit="showLoading()">
            <label for="url">Enter YouTube URL</label>
            <input type="text" name="url" id="url" required>
            <input type="submit" value="Download">
        </form>
        <div class="loading">
            <i class="fas fa-spinner fa-spin"></i> Processing...
        </div>
        <footer>
            Made by <b>Dev</b>
        </footer>
    </div>

    <script>
        function showLoading() {
            document.querySelector('.loading').style.display = 'block';
        }

        function toggleDarkMode() {
            const body = document.body;
            if (body.style.backgroundColor === 'white') {
                body.style.backgroundColor = '#121212';
                body.style.color = '#FFFFFF';
                localStorage.setItem('darkMode', 'enabled');
            } else {
                body.style.backgroundColor = 'white';
                body.style.color = '#000000';
                localStorage.setItem('darkMode', 'disabled');
            }
        }

        // Save dark mode setting in localStorage
        window.onload = function() {
            const darkMode = localStorage.getItem('darkMode');
            if (darkMode === 'enabled') {
                document.body.style.backgroundColor = '#121212';
                document.body.style.color = '#FFFFFF';
            } else {
                document.body.style.backgroundColor = 'white';
                document.body.style.color = '#000000';
            }
        }
    </script>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/js/all.min.js"></script>
</body>
</html>
    ''')

# Route to handle video download
@app.route('/download', methods=['POST'])
def download():
    video_url = request.form['url']
    try:
        file_path = download_video(video_url)
        
        # Start a thread to delete the file after 1 minute
        threading.Thread(target=delete_file_after_delay, args=(file_path, 60)).start()

        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return f"Error: {e}"

# Run Flask server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)