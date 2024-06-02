from flask import Flask, request, render_template, jsonify, send_from_directory, Response
from PIL import Image
import os
import json
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

                    # Extract line position and ensure they are integers
                    x1, y1, x2, y2 = map(int, line_position)
                    
                    width, height = img.size
                    # use pythagorean theorem to calculate box height based on the diagonal distance between the two points
                    box_height = int(((x2 - x1)**2 + (y2 - y1)**2)**0.5)
                    box_width = int(box_height * 0.7054263566)

                    # Calculate left and right box coordinates
                    left_box = (
                        max(0, x1 - box_width),
                        max(0, y1),
                        x1,
                        min(height, y2)
                    )

                    right_box = (
                        x1,
                        max(0, y1),
                        min(width, x1 + box_width),
                        min(height, y2)
                    )

                    left_img = img.crop(left_box)
                    right_img = img.crop(right_box)

                    # get the page number from the image name
                    imageCount = int(image_name.split('.')[0][-3:])
                    fileType = image_name.split('.')[1]
                    rightPageIndex = (imageCount * 2) - 1

                    left_output_path = os.path.join(OUTPUT_FOLDER, f"{str(rightPageIndex - 1).zfill(3)}_page-{NAME_ARRAY[rightPageIndex - 1]}.{fileType}")
                    right_output_path = os.path.join(OUTPUT_FOLDER, f"{str(rightPageIndex).zfill(3)}_page-{NAME_ARRAY[rightPageIndex]}.{fileType}")

                    left_img.save(left_output_path)
                    right_img.save(right_output_path)

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

                # Extract line position and ensure they are integers
                x1, y1, x2, y2 = map(int, line_position)
                
                width, height = img.size
                # use pythagorean theorem to calculate box height based on the diagonal distance between the two points
                box_height = int(((x2 - x1)**2 + (y2 - y1)**2)**0.5)
                box_width = int(box_height * 0.7054263566)

                # Calculate left and right box coordinates
                left_box = (
                    max(0, x1 - box_width),
                    max(0, y1),
                    x1,
                    min(height, y2)
                )

                right_box = (
                    x1,
                    max(0, y1),
                    min(width, x1 + box_width),
                    min(height, y2)
                )

                left_img = img.crop(left_box)
                right_img = img.crop(right_box)

                # get the page number from the image name
                imageCount = int(image_name.split('.')[0][-3:])
                fileType = image_name.split('.')[1]
                rightPageIndex = (imageCount * 2) - 1

                left_output_path = os.path.join(OUTPUT_FOLDER, f"{str(rightPageIndex - 1).zfill(3)}_page-{NAME_ARRAY[rightPageIndex - 1]}.{fileType}")
                right_output_path = os.path.join(OUTPUT_FOLDER, f"{str(rightPageIndex).zfill(3)}_page-{NAME_ARRAY[rightPageIndex]}.{fileType}")

                left_img.save(left_output_path)
                right_img.save(right_output_path)

                states[image_name]['processed'] = True
                save_image_states(states)

                processed_images += 1
                yield f"data: {json.dumps((processed_images / total_images) * 100)}\n\n"
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
