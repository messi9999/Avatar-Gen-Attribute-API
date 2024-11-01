import sys
import os
import numpy as np
import cv2
import argparse
import time
from mtcnn.mtcnn import MTCNN

detector = MTCNN()

# Define HSV color ranges for eyes colors
class_name = ("Blue", "Blue Gray", "Brown", "Brown Gray", "Brown Black", "Green", "Green Gray", "Other")
EyeColor = {
    class_name[0]: ((0, 0, 139), (173, 216, 230)),
    class_name[1]: ((70, 130, 180), (176, 196, 222)),
    class_name[2]: ((101, 67, 33), (210, 180, 140)),
    class_name[3]: ((85, 65, 47), (169, 134, 112)),
    class_name[4]: ((39, 26, 17), (39, 26, 17)),
    class_name[5]: ((0, 100, 0), (144, 238, 144)),
    class_name[6]: ((85, 107, 47), (189, 183, 107))
}

def check_color(hsv, color):
    if (hsv[0] >= color[0][0]) and (hsv[0] <= color[1][0]) and (hsv[1] >= color[0][1]) and hsv[1] <= color[1][1] and (hsv[2] >= color[0][2]) and (hsv[2] <= color[1][2]):
        return True
    return False

# Define eye color category rules in HSV space
def find_class(hsv):
    color_id = 7  # Default to "Other"
    for i in range(len(class_name)-1):
        if check_color(hsv, EyeColor[class_name[i]]) == True:
            color_id = i
    return color_id

# Error handling and eye color detection
def eye_color(image):
    try:
        start_time = time.time()
        imgHSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, w = image.shape[0:2]
        imgMask = np.zeros((image.shape[0], image.shape[1], 1))

        result = detector.detect_faces(image)
        if not result:
            raise ValueError('No face detected in the image')

        bounding_box = result[0]['box']
        left_eye = result[0]['keypoints']['left_eye']
        right_eye = result[0]['keypoints']['right_eye']

        eye_distance = np.linalg.norm(np.array(left_eye)-np.array(right_eye))
        eye_radius = eye_distance / 15  # approximate
        
        cv2.circle(imgMask, left_eye, int(eye_radius), (255,255,255), -1)
        cv2.circle(imgMask, right_eye, int(eye_radius), (255,255,255), -1)

        eye_class = np.zeros(len(class_name), float)

        for y in range(h):
            for x in range(w):
                if imgMask[y, x] != 0:
                    eye_class[find_class(imgHSV[y, x])] += 1 

        main_color_index = np.argmax(eye_class[:len(eye_class)-1])
        total_vote = eye_class.sum()

        print(f"Inference time: {round(time.time() - start_time, 4)} seconds")

        print("\nDominant Eye Color: ", class_name[main_color_index])

        # Return dominant color and percentages for further use
        return {
            "dominant_color": class_name[main_color_index],
            "color_percentage": {class_name[i]: round(eye_class[i] / total_vote * 100, 2) for i in range(len(class_name))}
        }

    except Exception as e:
        print(f"Error during eye color detection: {e}")
        return None

def detect_eye_color(image_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"The file {image_path} does not exist.")

    # Check if the file is a valid image
    if not image_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
        raise ValueError(f"The file {image_path} is not a valid image format.")

    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Failed to load image {image_path}. It may be corrupted.")

    return eye_color(image)

if __name__ == '__main__':
    try:
        result = detect_eye_color("image/45.png")
        if result:
            print(result)
    except Exception as e:
        print(f"An error occurred: {e}")
