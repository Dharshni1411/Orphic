from flask import Flask, render_template, request
import cv2
import numpy as np
import os

app = Flask(__name__, template_folder='templates')

UPLOAD_FOLDER = 'uploads'  # Folder to store uploaded images
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Skin color analysis function remains unchanged
def skin_color_analysis(image_path):
    # ... (your implementation remains here)
    img = cv2.imread(image_path)

    if img is None:
        return "Image not found or cannot be loaded."
    
    # Convert the image to the LAB color space for better skin color detection
    lab_img = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    
    # Define color range thresholds for fair, dusky, and dark skin tones in LAB color space
    fair_skin_lower = np.array([0, 130, 130], dtype="uint8")
    fair_skin_upper = np.array([255, 185, 135], dtype="uint8")

    dusky_skin_lower = np.array([0, 135, 135], dtype="uint8")
    dusky_skin_upper = np.array([255, 200, 145], dtype="uint8")

    dark_skin_lower = np.array([0, 155, 140], dtype="uint8")
    dark_skin_upper = np.array([255, 205, 155], dtype="uint8")

    # Create masks for each skin tone
    fair_skin_mask = cv2.inRange(lab_img, fair_skin_lower, fair_skin_upper)
    dusky_skin_mask = cv2.inRange(lab_img, dusky_skin_lower, dusky_skin_upper)
    dark_skin_mask = cv2.inRange(lab_img, dark_skin_lower, dark_skin_upper)

    # Calculate the percentage of each skin tone in the image
    total_pixels = lab_img.shape[0] * lab_img.shape[1]
    fair_skin_percentage = (cv2.countNonZero(fair_skin_mask) / total_pixels) * 100
    dusky_skin_percentage = (cv2.countNonZero(dusky_skin_mask) / total_pixels) * 100
    dark_skin_percentage = (cv2.countNonZero(dark_skin_mask) / total_pixels) * 100

    # Classify the skin tone based on the percentages
    if fair_skin_percentage > dusky_skin_percentage and fair_skin_percentage > dark_skin_percentage:
        return "Fair"
    elif dusky_skin_percentage > fair_skin_percentage and dusky_skin_percentage > dark_skin_percentage:
        return "Dusky"
    else:
        return "Dark"

# Routes for rendering HTML templates

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/skin')
def skintone():
    return render_template('skin.html')

@app.route('/body')
def bodyshape():
    return render_template('body.html')

@app.route('/suggestions')
def suggestions():
    return render_template('suggestions.html')

# Route for skin color analysis
@app.route('/analyze', methods=['POST'])
def analyze_skin_color():
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.png')
        file.save(file_path)
        detected_skin_color = skin_color_analysis(file_path)
        return render_template('skin.html', detected_skin_color=detected_skin_color)


# Route for body shape analysis
@app.route('/body_shape_analysis', methods=['POST'])
def analyze_body_shape():
    bust = float(request.form['bust'])
    waist = float(request.form['waist'])
    hips = float(request.form['hips'])
    gender = request.form['gender']
    # Body shape analysis logic remains here
    # ...
    waist_to_hip_ratio = waist / hips
    bust_to_hip_ratio = bust / hips

    body_shape = ""

    if gender == "female":
        if waist_to_hip_ratio < 0.7 and bust_to_hip_ratio >= 0.85:
            body_shape = "Hourglass"
        elif waist_to_hip_ratio >= 0.7 and waist_to_hip_ratio < 0.8 and bust_to_hip_ratio < 0.85:
            body_shape = "Pear"
        elif waist_to_hip_ratio >= 0.7 and waist_to_hip_ratio < 0.8 and bust_to_hip_ratio >= 0.85:
            body_shape = "Inverted Triangle"
        elif waist_to_hip_ratio >= 0.8 and bust_to_hip_ratio < 0.85:
            body_shape = "Rectangle"
        else:
            body_shape = "Undefined"
    elif gender == "male":
        if waist_to_hip_ratio < 0.7:
            body_shape = "Rectangle"
        elif waist_to_hip_ratio >= 0.7 and waist_to_hip_ratio < 0.8 and bust_to_hip_ratio < 0.85:
            body_shape = "Triangle"
        elif waist_to_hip_ratio >= 0.7 and waist_to_hip_ratio < 0.8 and bust_to_hip_ratio >= 0.85:
            body_shape = "Trapezoid"
        else:
            body_shape = "Undefined"
    else:
        body_shape = "Not Applicable (Other)"


    # Render body.html with the analyzed body shape and gender
    return render_template('body.html', body_shape=body_shape, gender=gender)

# Route for getting suggestions based on analysis
@app.route('/get_suggestions', methods=['POST'])
def get_suggestions():
    # Fetching parameters from the form data
    detected_skin_color = request.form['skin_color']
    body_shape = request.form['body_shape']
    gender = request.form['gender']
    # Logic for suggestions based on parameters
    # ...
    suggestions = {
        ('Fair', 'Pear', 'Female'): {
            'images': ['fair.jpeg', 'pear.png'],
            'description': [
                'Description: People with a pear body shape have narrower shoulders than their hips.',
                'Common traits: Weight in buttocks, lower hips, and thighs.'
            ]
        },
        ('Dusky', 'Rectangle', 'Male'): {
            'images': ['dusky.jpeg', 'rectangle.png'],
            'description': [
                'Description: People with a rectangle body shape have similar hip and shoulder width.',
                'Common traits: Equal hip and shoulder width, lack of waist definition.'
            ]
        },
        ('Dark', 'Inverted Triangle', 'Female'): {
            'images': ['dark.jpeg', 'inverted_triangle.png'],
            'description': [
                'Description: People with an inverted triangle body shape have wider shoulders than their hips.',
                'Common traits: Weight in the upper body and stomach, larger chests, and narrow hips.'
            ]
        },
        ('Fair', 'Hourglass', 'Female'): {
            'images': ['fair.jpeg', 'hourglass.png'],
            'description': [
                'Description: People with an hourglass body shape have both top and bottom halves equally broad.',
                'Common traits: Smaller waist than the chest and hips.'
            ]
        },
        ('Dusky', 'Triangle', 'Male'): {
            'images': ['dusky.jpeg', 'triangle.png'],
            'description': [
                'Description: People with a triangle body shape have broader hips than their shoulders.',
                'Common traits: Wider hips and thighs compared to the shoulders and chest.'
            ]
        },
        # Add more conditions following a similar structure for other combinations
    }

    suggestions_data = suggestions.get((detected_skin_color, body_shape, gender))
    if suggestions_data:
        images = suggestions_data['images']
        description = suggestions_data['description']
    else:
        images = []
        description = ["No suggestions available."]

    # Render suggestions.html with the suggestions data
    return render_template('suggestions.html', detected_skin_color=detected_skin_color, body_shape=body_shape, gender=gender)

if __name__ == '__main__':
    app.run(debug=True)