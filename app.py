from flask import Flask, request, render_template, jsonify, send_from_directory
from PIL import Image
import os
import json

app = Flask(__name__)

IMAGE_FOLDER = 'images'
OUTPUT_FOLDER = 'output'
STATE_FILE = 'image_states.json'

# Add an array of strings
NAME_ARRAY = [
  "II",
  "III",
  "IV",
  "V",
  "VI",
  "VII",
  "VIII",
  "IX",
  "X",
  "1",
  "2",
  "3",
  "4",
  "5",
  "6",
  "7",
  "8",
  "9",
  "10",
  "11",
  "12",
  "13",
  "14",
  "15",
  "16",
  "17",
  "18",
  "19",
  "20",
  "21",
  "22",
  "23",
  "24",
  "25",
  "26",
  "27",
  "28",
  "29",
  "30",
  "31",
  "32",
  "33",
  "34",
  "35",
  "36",
  "37",
  "38",
  "39",
  "40",
  "41",
  "42",
  "43",
  "44",
  "45",
  "46",
  "47",
  "48",
  "49",
  "50",
  "51",
  "52",
  "53",
  "54",
  "55",
  "56",
  "57",
  "58",
  "59",
  "60",
  "61",
  "62",
  "63",
  "64",
  "65",
  "66",
  "67",
  "68",
  "69",
  "70",
  "71",
  "72",
  "73",
  "74",
  "75",
  "76",
  "77",
  "78",
  "79",
  "80",
  "81",
  "82",
  "83",
  "84",
  "85",
  "86",
  "87",
  "88",
  "89",
  "90",
  "91",
  "92",
  "93",
  "94",
  "95",
  "96",
  "97",
  "98",
  "99",
  "100",
  "101",
  "102",
  "103",
  "104",
  "105",
  "106",
  "107",
  "108",
  "109",
  "110",
  "111",
  "112",
  "113",
  "114",
  "115",
  "116",
  "117",
  "118",
  "119",
  "120",
  "121",
  "122",
  "123",
  "124",
  "125",
  "126",
  "127",
  "128",
  "129",
  "130",
  "131",
  "132",
  "133",
  "134",
  "135",
  "136",
  "137",
  "138",
  "139",
  "140",
  "141",
  "142",
  "143",
  "144",
  "145",
  "146",
  "147",
  "148",
  "149",
  "150",
  "151",
  "152",
  "153",
  "154",
  "155",
  "156",
  "157",
  "158",
  "159",
  "160",
  "161",
  "162",
  "163",
  "164",
  "165",
  "166",
  "167",
  "168",
  "169",
  "170",
  "171",
  "172",
  "173",
  "174",
  "175",
  "176",
  "177",
  "178",
  "179",
  "180",
  "181",
  "182",
  "183",
  "184",
  "185",
  "186",
  "187",
  "188",
  "189",
  "190",
  "191",
  "192",
  "193",
  "194",
  "195",
  "196",
  "197",
  "198",
  "199",
  "200",
  "201",
  "202",
  "203",
  "204",
  "205",
  "206",
  "207",
  "208",
  "209",
  "210",
  "211",
  "212",
  "213",
  "214",
  "215",
  "216",
  "217",
  "218",
  "219",
  "220",
  "221",
  "222",
  "223",
  "224",
  "225",
  "226",
  "227",
  "228",
  "229",
  "230",
  "231",
  "232",
  "233",
  "234",
  "235",
  "236",
  "237",
  "238",
  "239",
  "240",
  "241",
  "242",
  "243",
  "244",
  "245",
  "246",
  "247",
  "248",
  "249",
  "250",
  "251",
  "252",
  "253",
  "254",
  "255",
  "256",
  "257",
  "258",
  "259",
  "260",
  "261",
  "262",
  "263",
  "264",
  "265",
  "266",
  "267",
  "268",
  "269",
  "270",
  "271",
  "272",
  "273",
  "274",
  "275",
  "276",
  "277",
  "278",
  "279",
  "280",
  "281",
  "282",
  "283",
  "284",
  "285",
  "286",
  "287",
  "288",
  "289",
  "290",
  "291",
  "292",
  "293",
  "294",
  "295",
  "296",
  "297",
  "298",
  "299",
  "300",
  "301",
  "302",
  "303",
  "304",
  "305",
  "306",
  "307",
  "308",
  "309",
  "310",
  "311",
  "312",
  "313",
  "314",
  "315",
  "316",
  "317",
  "318",
  "319",
  "320",
  "321",
  "322",
  "323",
  "324",
  "325",
  "326",
  "327",
  "328",
  "329",
  "330",
  "331",
  "332",
  "333",
  "334",
  "335",
  "336",
  "337",
  "338",
  "339",
  "340",
  "341",
  "342",
  "343",
  "344",
  "345",
  "346",
  "347",
  "348",
  "349",
  "350",
  "351",
  "352",
  "353",
  "354",
  "355",
  "356",
  "357",
  "358",
  "359",
  "360",
  "361",
  "362",
  "363",
  "364",
  "365",
  "366",
  "367",
  "368",
  "369",
  "370",
  "371",
  "372",
  "373",
  "374",
  "375",
  "376",
  "377",
  "378",
  "379",
  "380",
  "381",
  "382",
  "383",
  "384",
  "385",
  "386",
  "387",
  "388",
  "389",
  "390",
  "391",
  "392",
  "393",
  "394",
  "395",
  "396",
  "397",
  "398",
  "399",
  "400",
  "401",
  "402",
  "403",
  "404",
  "405",
  "406",
  "407",
  "408",
  "409",
  "410",
  "411",
  "412",
  "413",
  "414",
  "415",
  "416",
  "417",
  "418",
  "419",
  "420",
  "421",
  "422",
  "423",
  "424",
  "425",
  "426",
  "427",
  "428",
  "429",
  "430",
  "431",
  "432",
  "433",
  "434",
  "435",
  "436",
  "437",
  "438",
  "439",
  "440",
  "441",
  "442",
  "443",
  "444",
  "445",
  "446",
  "447",
  "448",
  "449",
  "450",
  "451",
  "452",
  "453",
  "454",
  "455",
  "456",
  "457",
  "458",
  "459",
  "460",
  "461",
  "462",
  "463",
  "464",
  "465",
  "466",
  "467",
  "468",
  "469",
  "470",
  "471",
]

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
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error processing images: {e}")
        return "Processing error", 500
    
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