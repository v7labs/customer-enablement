"""
This Python file is a Flask web application designed to simulate a machine learning model server for testing purposes. It's referred to as a "Bring Your Own Model (BYOM) Testing Stub". 

The application has three main endpoints:
1. `/`: This is the home endpoint that returns a welcome message.
2. `/api/classes`: This endpoint returns a list of bounding box classes in a format compatible with V7. The classes include polygon, bounding box, tag, keypoint, line, cuboid, ellipse, and skeleton.
3. `/infer`: This endpoint simulates the inference process of a machine learning model. It returns a predefined set of test results in JSON format. If an exception occurs, it returns a status of "failed" and an empty results list.

The application is designed to run on the local machine on port 8080 and is set to debug mode.
"""

from flask import Flask, jsonify

# Initliazing Flask App
app = Flask(__name__)
...

# Initliazing Flask App
app = Flask(__name__)


@app.route("/")
def home():
    """Returns a welcome message for the Flask application.

    Returns:
        str: An HTML string that represents a welcome message.
    """
    return "<h1>Welcome to the Bring Your Own Model (BYOM) Testing Stub</h1>"


# End point that returns a list of all test classes in expected V7 format
@app.route("/api/classes", methods=["GET"])
def classes():
    """Returns a list of bounding box classes in V7 format.

    This function is a route in a Flask web application that is triggered
    when a GET request is made to the "/api/classes" URL. It returns a list
    of bounding box classes in a format that is compatible with V7.

    Returns:
        list: A list of dictionaries, each representing a bounding box class.
    """
    v7_list = [
        {"name": "test_polygon", "type": "polygon"},
        {"name": "test_bbox", "type": "bounding_box"},
        {"name": "test_tag", "type": "tag"},
        {"name": "test_keypoint", "type": "keypoint"},
        {"name": "test_line", "type": "line"},
        {"name": "test_cuboid", "type": "cuboid"},
        {"name": "test_ellipse", "type": "ellipse"},
        {"name": "test_skeleton", "type": "skeleton"},
    ]

    return jsonify(v7_list)


test_results = [
    {
        "confidence": 1,
        "label": "test_polygon",
        "name": "test_polygon",
        "polygon": {
            "path": [
                {"x": 677.0, "y": 896.0},
                {"x": 676.0, "y": 896.0},
                {"x": 675.0, "y": 897.0},
                {"x": 674.0, "y": 897.0},
                {"x": 675.0, "y": 897.0},
                {"x": 676.0, "y": 898.0},
                {"x": 675.0, "y": 899.0},
                {"x": 674.0, "y": 899.0},
                {"x": 671.0, "y": 902.0},
            ]
        },
    },
    {
        "confidence": 1,
        "label": "test_bbox",
        "name": "test_bbox",
        "bounding_box": {"h": 400, "w": 300, "x": 550, "y": 120},
    },
    {"confidence": 1, "label": "test_tag", "name": "test_tag", "tag": {}},
    {
        "confidence": 1,
        "label": "test_keypoint",
        "name": "test_keypoint",
        "keypoint": {"x": 550, "y": 120},
    },
    {
        "confidence": 1,
        "label": "test_line",
        "name": "test_line",
        "line": {
            "path": [
                {"x": 25.79, "y": 135.3},
                {"x": 52.92, "y": 124.51},
                {"x": 60.31, "y": 141.77},
                {"x": 36.89, "y": 173.83},
                {"x": 35.66, "y": 154.41},
                {"x": 25.79, "y": 134.38},
                {"x": 81.27, "y": 143.01},
                {"x": 38.12, "y": 122.97},
                {"x": 25.79, "y": 134.38},
            ]
        },
    },
    {
        "confidence": 1,
        "label": "test_cuboid",
        "name": "test_cuboid",
        "cuboid": {
            "back": {"h": 0.62, "w": 0.92, "x": 222.74, "y": 28.97},
            "front": {"h": 32.67, "w": 58.87, "x": 216.57, "y": 6.78},
        },
    },
    {
        "confidence": 1,
        "label": "test_skeleton",
        "name": "test_skeleton",
        "skeleton": {
            "nodes": [
                {"name": "1", "occluded": False, "x": 130.4, "y": 160.25},
                {"name": "2", "occluded": False, "x": 198.63, "y": 161.18},
                {"name": "3", "occluded": False, "x": 216.19, "y": 182.97},
                {"name": "4", "occluded": False, "x": 215.86, "y": 134.1},
                {"name": "5", "occluded": False, "x": 120.27, "y": 136.59},
            ]
        },
    },
    {
        "confidence": 1,
        "label": "test_ellipse",
        "name": "test_ellipse",
        "ellipse": {
            "angle": 0.73,
            "center": {"x": 49.83, "y": 34.21},
            "radius": {"x": 30.56, "y": 30.56},
        },
    },
]


# Inference endpoint for the Flask app
@app.route("/infer", methods=["POST"])
def infer():
    """Handles inference requests to the model.

    This function is a route in a Flask web application that is triggered
    when a POST request is made to the "/infer" URL. It attempts to return
    a JSON response with the status and test results. If an exception occurs,
    it returns a JSON response with a status of "failed" and an empty results list.

    Returns:
        Response: A Flask Response object containing a JSON response.
    """
    try:
        return jsonify(status="succeeded", results=test_results)
    except Exception as e:
        return jsonify(status="failed", results=[e])


# Run Flask App
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
