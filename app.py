from flask import Flask, request, render_template, jsonify, send_from_directory, Response
from PIL import Image
import os
import json
import math
import time

app = Flask(__name__)

IMAGE_FOLDER = 'images'
OUTPUT_FOLDER = 'output'
STATE_FILE = 'image_states.json'

# Condensed array starting with roman numerals II to X and then numbers from 1 to 471
NAME_ARRAY = ["II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"] + [str(i) for i in range(1, 472)]

def load_image_states():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_image_states(states):
    with open(STATE_FILE, 'w') as f:
        json.dump(states, f)


def rotate_image_and_crop(img, line_position, angle, is_right_page):
    """ Rotate the image and the bounding box and then crop it. """
    width, height = img.size
    cx, cy = width / 2, height / 2

    adjusted_angle = angle - 90

    # Rotate the image around its center
    rotated_img = img.rotate(adjusted_angle, center=(cx, cy), resample=Image.BICUBIC, expand=True)

    point1 = rotate_point(line_position[0], line_position[1], cx, cy, adjusted_angle)
    point2 = rotate_point(line_position[2], line_position[3], cx, cy, adjusted_angle)

    # Calculate the new bounding box
    x1, y1 = point1
    x2, y2 = point2
    box_height = int(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))
    box_width = int(box_height * 0.7054263566)

    # crop the rotated image by the new bounding box
    cropped_img = rotated_img.crop((x1, y1, x1 + box_width, y2)) if is_right_page else rotated_img.crop((x1 - box_width, y1, x1, y2))

    return cropped_img

def rotate_point(x, y, cx, cy, angle):
    """ Rotate a point around a center with a given angle in degrees. """
    radians = math.radians(angle)
    dx = x - cx
    dy = y - cy
    nx = dx * math.cos(radians) - dy * math.sin(radians)
    ny = dx * math.sin(radians) + dy * math.cos(radians)
    return cx + nx, cy + ny

@app.route('/')
def index():
    images = [img for img in os.listdir(IMAGE_FOLDER) if img.endswith(('png', 'jpg', 'jpeg'))]
    images.sort()
    image_states = load_image_states()
    return render_template('index.html', images=images, image_states=image_states)

@app.route('/images/<filename>')
def serve_image(filename):
    try:
        return send_from_directory(IMAGE_FOLDER, filename)
    except Exception as e:
        print(f"Error serving image {filename}: {e}")
        return "Image not found", 404

@app.route('/save_state', methods=['POST'])
def save_state():
    try:
        data = request.json
        image_name = data['image']
        line_position = data['line_position']

        states = load_image_states()
        states[image_name] = {
            'line_position': line_position,
            'processed': False
        }
        save_image_states(states)
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error saving state: {e}")
        return "Saving state error", 500

@app.route('/process', methods=['POST'])
def process_images():
    try:
        states = load_image_states()
        total_images = len([s for s in states.values() if not s['processed']])
        processed_images = 0

        def generate():
            nonlocal processed_images
            for image_name, state in states.items():
                if not state['processed']:
                    line_position = state['line_position']

                    image_path = os.path.join(IMAGE_FOLDER, image_name)
                    if not os.path.exists(image_path):
                        print(f"Image path does not exist: {image_path}")
                        continue

                    img = Image.open(image_path)
                    width, height = img.size

                    # Extract line position and ensure they are integers
                    x1, y1, x2, y2 = map(int, line_position)
                    box_height = int(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))
                    box_width = int(box_height * 0.7054263566)

                    # Calculate angle for rotation
                    angle = math.degrees(math.atan2(y2 - y1, x2 - x1))

                    # Calculate new bounding boxes
                    left_bbox = [(x1 - box_width, y1), (x1, y1), (x1 - box_width, y2), (x1, y2)]
                    right_bbox = [(x1, y1), (x1 + box_width, y1), (x1, y2), (x1 + box_width, y2)]

                    # Crop rotated images
                    left_img = rotate_image_and_crop(img, [x1,y1,x2,y2], angle, 0)
                    right_img = rotate_image_and_crop(img, [x1,y1,x2,y2], angle, 1)

                    # Get the page number from the image name
                    image_count = int(image_name.split('.')[0][-3:])
                    file_type = image_name.split('.')[1]
                    right_page_index = (image_count * 2) - 1

                    left_output_path = os.path.join(OUTPUT_FOLDER, f"{str(right_page_index - 1).zfill(3)}_page-{NAME_ARRAY[right_page_index - 1]}.{file_type}")
                    right_output_path = os.path.join(OUTPUT_FOLDER, f"{str(right_page_index).zfill(3)}_page-{NAME_ARRAY[right_page_index]}.{file_type}")

                    left_img.save(left_output_path)
                    print(f"{left_output_path} Processed")
                    right_img.save(right_output_path)
                    print(f"{right_output_path} Processed")

                    states[image_name]['processed'] = True
                    save_image_states(states)

                    processed_images += 1
                    yield f"data: {json.dumps((processed_images / total_images) * 100)}\n\n"
                    time.sleep(0.1)

            yield "data: 100\n\n"

        return Response(generate(), mimetype='text/event-stream')
    except Exception as e:
        print(f"Error processing images: {e}")
        return "Processing error", 500

@app.route('/progress')
def progress():
    def generate():
        states = load_image_states()
        total_images = len([s for s in states.values() if not s['processed']])
        processed_images = 0
        while processed_images < total_images:
            processed_images = len([s for s in states.values() if s['processed']])
            yield f"data: {(processed_images / total_images) * 100}\n\n"
            time.sleep(0.1)
        yield "data: 100\n\n"
    return Response(generate(), mimetype='text/event-stream')

@app.route('/reset', methods=['POST'])
def reset_processed():
    try:
        states = load_image_states()
        for state in states.values():
            state['processed'] = False
        save_image_states(states)
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error resetting states: {e}")
        return "Reset error", 500

if __name__ == '__main__':
    app.run(debug=True)
