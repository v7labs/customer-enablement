"""
Script name: hugging_face_object_detection.py

DESCRIPTION
When executed, this script:
- Sets up a Flask application that exposes endpoints for performing object detection using a Hugging Face model.
- The endpoints allow for getting the list of classes the model can detect and for performing inference on an image.

USAGE
Run the script in a Python environment where Flask is installed. The application will start on port 8080.

GLOBAL VARIABLES
- MODEL_ID: The ID of the Hugging Face model to use for inference.
- API_TOKEN: The API token for authenticating with the Hugging Face API.
- OBJ_CLASSES_DICT: A dictionary mapping class IDs to class names for the model.
"""

import base64
import io
import json
import requests
import tempfile
import urllib
from flask import Flask, request, jsonify
from PIL import Image

# Global Variables
MODEL_ID = "facebook/detr-resnet-50"
API_TOKEN = "<Hugging Face API Key>"

# Resnet50 Object Classes
obj_classes_dict = {
    "0": "N/A",
    "1": "person",
    "10": "traffic light",
    "11": "fire hydrant",
    "12": "street sign",
    "13": "stop sign",
    "14": "parking meter",
    "15": "bench",
    "16": "bird",
    "17": "cat",
    "18": "dog",
    "19": "horse",
    "2": "bicycle",
    "20": "sheep",
    "21": "cow",
    "22": "elephant",
    "23": "bear",
    "24": "zebra",
    "25": "giraffe",
    "26": "hat",
    "27": "backpack",
    "28": "umbrella",
    "29": "shoe",
    "3": "car",
    "30": "eye glasses",
    "31": "handbag",
    "32": "tie",
    "33": "suitcase",
    "34": "frisbee",
    "35": "skis",
    "36": "snowboard",
    "37": "sports ball",
    "38": "kite",
    "39": "baseball bat",
    "4": "motorcycle",
    "40": "baseball glove",
    "41": "skateboard",
    "42": "surfboard",
    "43": "tennis racket",
    "44": "bottle",
    "45": "plate",
    "46": "wine glass",
    "47": "cup",
    "48": "fork",
    "49": "knife",
    "5": "airplane",
    "50": "spoon",
    "51": "bowl",
    "52": "banana",
    "53": "apple",
    "54": "sandwich",
    "55": "orange",
    "56": "broccoli",
    "57": "carrot",
    "58": "hot dog",
    "59": "pizza",
    "6": "bus",
    "60": "donut",
    "61": "cake",
    "62": "chair",
    "63": "couch",
    "64": "potted plant",
    "65": "bed",
    "66": "mirror",
    "67": "dining table",
    "68": "window",
    "69": "desk",
    "7": "train",
    "70": "toilet",
    "71": "door",
    "72": "tv",
    "73": "laptop",
    "74": "mouse",
    "75": "remote",
    "76": "keyboard",
    "77": "cell phone",
    "78": "microwave",
    "79": "oven",
    "8": "truck",
    "80": "toaster",
    "81": "sink",
    "82": "refrigerator",
    "83": "blender",
    "84": "book",
    "85": "clock",
    "86": "vase",
    "87": "scissors",
    "88": "teddy bear",
    "89": "hair drier",
    "9": "boat",
    "90": "toothbrush",
}


# Models Section
def model_query(data, model_id, api_token):
    """
    Sends file for inference to the specified Hugging Face model.

    Parameters
    ----------
    data : bytes
        The data to send for inference.
    model_id : str
        The ID of the Hugging Face model to use for inference.
    api_token : str
        The API token for authenticating with the Hugging Face API.

    Returns
    -------
    response : Dict[str, Any]
        A dictionary containing the response from the Hugging Face API.
    """
    headers = {"Authorization": f"Bearer {api_token}"}
    API_URL = f"https://api-inference.huggingface.co/models/{model_id}"
    response = requests.request("POST", API_URL, headers=headers, data=data)
    return json.loads(response.content.decode("utf-8"))


# Flask App
app = Flask(__name__)


def resolve_image(image_spec: dict[str, str]) -> Image:
    """
    Resolves a presigned URL or base64 encoded image into an Image object.

    Parameters
    ----------
    image_spec : Dict[str, str]
        A dictionary containing either a "url" key with a presigned URL as the value,
        or a "base64" key with a base64 encoded image as the value.

    Returns
    -------
    image : Image
        An Image object that can be processed by a model.
    """

    if "url" in image_spec:
        with tempfile.NamedTemporaryFile() as file:
            urllib.request.urlretrieve(image_spec["url"], file.name)
            return Image.open(file.name).convert("RGB")
    elif "base64" in image_spec:
        with tempfile.NamedTemporaryFile() as file:
            file.write(base64.decodebytes(image_spec["base64"].encode("utf-8")))
            return Image.open(file.name).convert("RGB")
    else:
        raise ValueError("Invalid image spec")


def url_to_binary(url):
    """
    Converts a presigned URL into binary data representing the image.

    Parameters
    ----------
    url : str
        The presigned URL of the image.

    Returns
    -------
    binary_data : bytes
        The binary data representing the image.
    """
    urllib.request.urlretrieve(url, "temp")
    img = Image.open("temp").convert("RGB")
    output = io.BytesIO()
    img.save(output, format="JPEG")
    hex_data = output.getvalue()
    return hex_data


# V7 Results Extraction
def v7_results(resultos):
    """
    Transforms the inference results from the Hugging Face model into a format compatible with V7's Bring Your Own Model (BYOM) format.

    Parameters
    ----------
    resultos : List[Dict[str, Any]]
        The inference results from the Hugging Face model.

    Returns
    -------
    v7results : List[Dict[str, Any]]
        A list of dictionaries where each dictionary represents an object detected in the image. Each dictionary contains the label of the object, its confidence score, and its bounding box coordinates.
    """
    nupdres = resultos

    v7results = []
    for res in nupdres:
        temp_dict = {}
        temp_bb = {}

        box = res["box"]

        temp_bb["h"] = box["ymax"] - box["ymin"]
        temp_bb["w"] = box["xmax"] - box["xmin"]
        temp_bb["x"] = box["xmin"]
        temp_bb["y"] = box["ymin"]

        temp_dict["confidence"] = res["score"]
        temp_dict["label"] = res["label"]
        temp_dict["name"] = res["label"]
        temp_dict["bounding_box"] = temp_bb

        v7results.append(temp_dict)

    return v7results


@app.route("/")
def home():
    return "<h1>Test Home Page</h1>"


@app.route("/api/classes", methods=["GET"])
def classes():
    """
    Returns a list of bounding box classes for use in V7 Bring Your Own Model.

    Returns
    -------
    response : str
        A JSON string containing a list of classes as expected by the V7 format.
    """
    returned_classes = list(obj_classes_dict.values())
    v7_list = []

    for clas in returned_classes:
        temp_dict = {}
        temp_dict["name"] = clas
        temp_dict["type"] = "bounding_box"
        v7_list.append(temp_dict)

    return jsonify(v7_list)


@app.route("/infer", methods=["POST"])
def infer():
    """
    Performs inference on an image using the hugging face resnet50 model.

    Raises
    ------
    ValueError
        If the image is not a valid Image object or the model is None.

    Returns
    -------
    results : Dict[str, Any]
        A dictionary containing the results of the inference.
    """
    payload = request.json

    try:
        assert payload["image"]["url"] == str, "Please ensure valid image URL"
        image = url_to_binary(payload["image"]["url"])
        model_results = model_query(image, MODEL_ID, API_TOKEN)
        converted_results = v7_results(model_results)

        return jsonify(status="succeeded", results=converted_results)
    except Exception as e:
        return jsonify(status="failed", results=[e])


# Run Flask App
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
