import os
import time
import requests
import cv2
import numpy as np
from cv2 import dnn
import hashlib
import logging

# Set up logging for the application
logging.basicConfig(level=logging.INFO)

# Paths to model files
args_caffe_prototxt_path = "app/models/face_model/RFB-320/RFB-320.prototxt"
args_caffe_model_path = "app/models/face_model/RFB-320/RFB-320.caffemodel"
args_onnx_path = "app/models/face_model/onnx/version-RFB-320_simplified.onnx"

# caffe_prototxt_folder= "app/models/face_model/RFB-320/"
# caffe_model_folder = "app/models/face_model/RFB-320/"
# onnx_folder = "app/models/face_model/onnx/"

# caffe_prototxt_url = "https://github.com/Linzaer/Ultra-Light-Fast-Generic-Face-Detector-1MB/blob/master/caffe/model/RFB-320/RFB-320.prototxt"
# caffe_model_url = "https://github.com/Linzaer/Ultra-Light-Fast-Generic-Face-Detector-1MB/blob/master/caffe/model/RFB-320/RFB-320.caffemodel"
onnx_url = "https://raw.githubusercontent.com/Linzaer/Ultra-Light-Fast-Generic-Face-Detector-1MB/master/models/onnx/version-RFB-320_simplified.onnx"




# Parameters
args_input_size = "320,240"
args_threshold = 0.7
image_mean = np.array([127, 127, 127])
image_std = 128.0
iou_threshold = 0.3
center_variance = 0.1
size_variance = 0.2
min_boxes = [[10.0, 16.0, 24.0], [32.0, 48.0], [64.0, 96.0], [128.0, 192.0, 256.0]]
strides = [8.0, 16.0, 32.0, 64.0]
MAX_SIZE = (1024, 1024)  # Maximum allowed image size

# Verifying the model's integrity using SHA-256
def verify_model(path, expected_hash):   
    sha256 = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    if sha256.hexdigest() != expected_hash:
        raise ValueError(f"Model file {path} is corrupted or tampered with.")
    logging.info(f"Model {path} has been verified successfully.")

# Define input image size
def define_img_size(image_size):
    shrinkage_list = []
    feature_map_w_h_list = []
    for size in image_size:
        feature_map = [int(np.ceil(size / stride)) for stride in strides]
        feature_map_w_h_list.append(feature_map)
    for i in range(0, len(image_size)):
        shrinkage_list.append(strides)
    priors = generate_priors(feature_map_w_h_list, shrinkage_list, image_size, min_boxes)
    return priors

# Generate prior boxes for face detection
def generate_priors(feature_map_list, shrinkage_list, image_size, min_boxes):
    priors = []
    for index in range(0, len(feature_map_list[0])):
        scale_w = image_size[0] / shrinkage_list[0][index]
        scale_h = image_size[1] / shrinkage_list[1][index]
        for j in range(0, feature_map_list[1][index]):
            for i in range(0, feature_map_list[0][index]):
                x_center = (i + 0.5) / scale_w
                y_center = (j + 0.5) / scale_h
                for min_box in min_boxes[index]:
                    w = min_box / image_size[0]
                    h = min_box / image_size[1]
                    priors.append([x_center, y_center, w, h])
    logging.info(f"Priors generated: {len(priors)} boxes")
    return np.clip(priors, 0.0, 1.0)

# Hard Non-Maximum Suppression (NMS) to filter overlapping boxes
def hard_nms(box_scores, iou_threshold, top_k=-1, candidate_size=200):
    scores = box_scores[:, -1]
    boxes = box_scores[:, :-1]
    picked = []
    indexes = np.argsort(scores)
    indexes = indexes[-candidate_size:]
    while len(indexes) > 0:
        current = indexes[-1]
        picked.append(current)
        if 0 < top_k == len(picked) or len(indexes) == 1:
            break
        current_box = boxes[current, :]
        indexes = indexes[:-1]
        rest_boxes = boxes[indexes, :]
        iou = iou_of(rest_boxes, np.expand_dims(current_box, axis=0))
        indexes = indexes[iou <= iou_threshold]
    return box_scores[picked, :]

# Calculate area of the boxes
def area_of(left_top, right_bottom):
    hw = np.clip(right_bottom - left_top, 0.0, None)
    return hw[..., 0] * hw[..., 1]

# Calculate Intersection over Union (IoU) of two boxes
def iou_of(boxes0, boxes1, eps=1e-5):
    overlap_left_top = np.maximum(boxes0[..., :2], boxes1[..., :2])
    overlap_right_bottom = np.minimum(boxes0[..., 2:], boxes1[..., 2:])
    overlap_area = area_of(overlap_left_top, overlap_right_bottom)
    area0 = area_of(boxes0[..., :2], boxes0[..., 2:])
    area1 = area_of(boxes1[..., :2], boxes1[..., 2:])
    return overlap_area / (area0 + area1 - overlap_area + eps)

# Predict the bounding boxes and labels
def predict(width, height, confidences, boxes, prob_threshold, iou_threshold=0.3, top_k=-1):
    boxes = boxes[0]
    confidences = confidences[0]
    picked_box_probs = []
    picked_labels = []
    for class_index in range(1, confidences.shape[1]):
        probs = confidences[:, class_index]
        mask = probs > prob_threshold
        probs = probs[mask]
        if probs.shape[0] == 0:
            continue
        subset_boxes = boxes[mask, :]
        box_probs = np.concatenate([subset_boxes, probs.reshape(-1, 1)], axis=1)
        box_probs = hard_nms(box_probs, iou_threshold=iou_threshold, top_k=top_k)
        picked_box_probs.append(box_probs)
        picked_labels.extend([class_index] * box_probs.shape[0])
    if not picked_box_probs:
        return np.array([]), np.array([]), np.array([])
    picked_box_probs = np.concatenate(picked_box_probs)
    picked_box_probs[:, 0] *= width
    picked_box_probs[:, 1] *= height
    picked_box_probs[:, 2] *= width
    picked_box_probs[:, 3] *= height
    return picked_box_probs[:, :4].astype(np.int32), np.array(picked_labels), picked_box_probs[:, 4]

# Convert center form to corner form of bounding boxes
def convert_locations_to_boxes(locations, priors, center_variance, size_variance):
    if len(priors.shape) + 1 == len(locations.shape):
        priors = np.expand_dims(priors, 0)
    return np.concatenate([
        locations[..., :2] * center_variance * priors[..., 2:] + priors[..., :2],
        np.exp(locations[..., 2:] * size_variance) * priors[..., 2:]
    ], axis=len(locations.shape) - 1)

# Convert center format of boxes to corner format
def center_form_to_corner_form(locations):
    return np.concatenate([locations[..., :2] - locations[..., 2:] / 2,
                           locations[..., :2] + locations[..., 2:] / 2], len(locations.shape) - 1)

# Main function to detect faces
def detect_face(image_path):
    try:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image path does not exist: {image_path}")
        if not image_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            raise ValueError(f"Unsupported file format for {image_path}")

        # Check image size to avoid excessively large images
        img_ori = cv2.imread(image_path)
        if img_ori.shape[0] > MAX_SIZE[0] or img_ori.shape[1] > MAX_SIZE[1]:
            raise ValueError("Image exceeds maximum allowed size")

        # Read and verify model
        # verify_model(args_onnx_path, "expected_onnx_model_hash")
        if not os.path.exists(args_onnx_path):
            # Send a GET request to the URL
            response = requests.get(onnx_url, stream=True)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Write the file contents to the local file
                with open(args_onnx_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                print(f"File downloaded successfully: {args_onnx_path}")
            else:
                print(f"Failed to download file. Status code: {response.status_code}")
        else:
            print(f"File already exists: {args_onnx_path}")
        
        net = dnn.readNetFromONNX(args_onnx_path)

        input_size = [int(v.strip()) for v in args_input_size.split(",")]
        width = input_size[0]
        height = input_size[1]
        priors = define_img_size(input_size)

        rect = cv2.resize(img_ori, (width, height))
        rect = cv2.cvtColor(rect, cv2.COLOR_BGR2RGB)
        net.setInput(dnn.blobFromImage(rect, 1 / image_std, (width, height), 127))
        start_time = time.time()
        boxes, scores = net.forward(["boxes", "scores"])
        logging.info(f"Inference time: {round(time.time() - start_time, 4)} seconds")

        boxes = np.expand_dims(np.reshape(boxes, (-1, 4)), axis=0)
        scores = np.expand_dims(np.reshape(scores, (-1, 2)), axis=0)
        boxes = convert_locations_to_boxes(boxes, priors, center_variance, size_variance)
        boxes = center_form_to_corner_form(boxes)
        boxes, labels, probs = predict(img_ori.shape[1], img_ori.shape[0], scores, boxes, args_threshold)

        if boxes.shape[0] == 0:
            logging.info("No face detected")
            return False
        else:
            logging.info(f"Found {boxes.shape[0]} faces")
            for i in range(boxes.shape[0]):
                box = boxes[i, :]
                cv2.rectangle(img_ori, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)

            # # Show the detected faces
            # cv2.imshow("Face Detection", img_ori)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
            return True

    except Exception as e:
        logging.error(f"Error during face detection: {e}")
        return False


if __name__ == '__main__':
    detect_face("image/42.jpg")
