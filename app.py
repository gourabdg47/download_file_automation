from flask import Flask, render_template
from file_organizer import start_file_observer

app = Flask(__name__)

# Start the file observer in a separate thread
# start_file_observer()

# Assuming you have 'categories' and 'file_counts' lists
categories = ["Images", "Videos", "Music", "Softwares", "SFX", "Docs"]
file_counts = [10, 5, 8, 12, 3, 6]

@app.route('/')
def index():
    # Zip the two lists
    zipped_data = zip(categories, file_counts)
    return render_template('index.html', zipped_data=zipped_data)

if __name__ == '__main__':
    app.run(debug=True)
