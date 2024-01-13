from flask import Flask, render_template
from file_organizer import DEFAULT_DOWNLOAD_PATH, FileMoveHandler, start_file_observer

import logging

app = Flask(__name__)

# Configure Flask app logger
app.logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler = logging.FileHandler('flask_app.log')
file_handler.setFormatter(formatter)
app.logger.addHandler(file_handler)

@app.route('/')
def index():
    app.logger.info('Accessing index page')
    return render_template('index.html', 
                           source_path=DEFAULT_DOWNLOAD_PATH)

@app.route('/start_observer', methods=['GET', 'POST'])
def start_observer():
    app.logger.info('Starting file observer')
    start_file_observer()
    return 'File observer started successfully.'


if __name__ == "__main__":
    app.run(debug=True)
