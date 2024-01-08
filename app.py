from flask import Flask, render_template, request, redirect, url_for
import os
from parallax import create_parallax  # Import the function from your script

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename != '':
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
                photo.save(filepath)
                gif_path = create_parallax(filepath, int(request.form.get('num_frames', 30)))
                return url_for('static', filename=gif_path[len('static/'):])  # Return the path of the GIF
    return render_template('index.html')

@app.route('/result/<img_name>', methods=['GET', 'POST'])
def result(img_name):
    num_frames = request.form.get('num_frames', 30)  # Default to 30 frames
    gif_path = create_parallax(os.path.join(app.config['UPLOAD_FOLDER'], img_name), int(num_frames))
    return render_template('result.html', gif_path=gif_path)

if __name__ == '__main__':
    app.run(debug=True)
