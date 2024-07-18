import json
import numpy as np
import cv2
import os
import requests

# Define the directory containing the JSON files
json_directory = '/Users/jameshudson/Downloads/convert-this-mask'
output_directory = '/Users/jameshudson/Desktop/Masks'

# Ensure the output directory exists
os.makedirs(output_directory, exist_ok=True)

# API call to fetch annotation classes
def fetch_annotation_classes(api_key, team_slug_or_id):
    url = f"https://darwin.v7labs.com/api/teams/{team_slug_or_id}/annotation_classes"
    headers = {
        "accept": "application/json",
        "Authorization": f"ApiKey {api_key}"
    }
    response = requests.get(url, headers=headers)
    return response.json()

# Convert RGBA color from API to BGR for OpenCV
def rgba_to_bgr(rgba):
    rgba = rgba.replace("rgba(", "").replace(")", "")
    r, g, b, a = map(float, rgba.split(","))
    return (int(b), int(g), int(r))

# Fetch annotation classes and create a mapping from class names to colors
api_key = "Mr3eWOs.yLMr08Srs85SIfgU1OBVVzpkYFdatpFK"
team_slug_or_id = "cv-central-2-point-zero"
annotation_classes = fetch_annotation_classes(api_key, team_slug_or_id)['annotation_classes']

color_map = {}
for annotation_class in annotation_classes:
    class_name = annotation_class['name']
    color_rgba = annotation_class['metadata'].get('_color', 'rgba(255,255,255,1.0)')
    color_map[class_name] = rgba_to_bgr(color_rgba)

# Process each JSON file in the directory
for json_filename in os.listdir(json_directory):
    if json_filename.endswith('.json'):
        json_path = os.path.join(json_directory, json_filename)
        
        with open(json_path, 'r') as file:
            data = json.load(file)
        
        # Extract image dimensions
        width = data['item']['slots'][0]['width']
        height = data['item']['slots'][0]['height']

        # Create a black background
        mask = np.zeros((height, width, 3), dtype=np.uint8)

        # Find the raster layer annotation
        raster_layer = None
        for annotation in data['annotations']:
            if 'raster_layer' in annotation:
                raster_layer = annotation['raster_layer']
                break

        if raster_layer:
            print(f"Processing raster layer for {json_filename}")
            # Extract dense RLE and mask annotation ids mapping
            dense_rle = raster_layer['dense_rle']
            mask_annotation_ids_mapping = raster_layer['mask_annotation_ids_mapping']
            total_pixels = raster_layer['total_pixels']
            print(f"Total pixels: {total_pixels}")

            # Create a flat mask array
            flat_mask = np.zeros(total_pixels, dtype=np.uint8)

            current_position = 0
            for i in range(0, len(dense_rle), 2):
                value = dense_rle[i]
                count = dense_rle[i+1]
                if value != 0:  # 0 is for free space
                    flat_mask[current_position:current_position+count] = value
                current_position += count

            # Map flat mask to 2D mask
            mask_2d = flat_mask.reshape((height, width))
            print(f"Flat mask mapped to 2D mask with shape: {mask_2d.shape}")

            # Apply colors to the mask based on annotation ids
            for annotation_id, mask_value in mask_annotation_ids_mapping.items():
                class_name = next((ann['name'] for ann in data['annotations'] if ann['id'] == annotation_id), None)
                if class_name:
                    color = color_map.get(class_name, (255, 255, 255))  # Default to white if class name not found
                    mask[mask_2d == mask_value] = color
                    print(f"Color {color} applied to class: {class_name}")

        else:
            print(f"No raster layer found for {json_filename}")

        # Save the semantic mask image with the same base name as the JSON file
        output_filename = os.path.splitext(json_filename)[0] + '_mask.png'
        output_path = os.path.join(output_directory, output_filename)
        cv2.imwrite(output_path, mask)
        print(f'Semantic mask saved to {output_path}')


