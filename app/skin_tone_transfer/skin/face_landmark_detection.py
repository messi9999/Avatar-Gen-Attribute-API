import sys
import os
import dlib
import glob
import numpy as np
from skimage import io
import requests

shape_url = "https://raw.githubusercontent.com/italojs/facial-landmarks-recognition/blob/master/shape_predictor_68_face_landmarks.dat"

# This function is meant to give coordinates of both eyes and mouth so skin detection can work better.
def getEyesMouth(img):

    # Compile the facial landmarks predictor.
    predictor_path = "shape_predictor_68_face_landmarks.dat"
    if not os.path.exists(predictor_path):
        # Send a GET request to the URL
        response = requests.get(shape_url, stream=True)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Write the file contents to the local file
            with open(predictor_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"File downloaded successfully: {predictor_path}")
        else:
            print(f"Failed to download file. Status code: {response.status_code}")
    else:
        print(f"File already exists: {predictor_path}")
        
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(predictor_path)

    # Ask the detector to find the bounding boxes of each face. The 1 in the
    # second argument indicates that we should upsample the image 1 time. This
    # will make everything bigger and allow us to detect more faces.
    dets = detector(img, 1)
    # print("Number of faces detected: {}".format(len(dets)))

    # Make lists for storing the coordinates.
    leyeList=[]
    reyeList=[]
    mouthList=[]

    # Apply a for loop for more than one face in the image
    for k, d in enumerate(dets):

        # Get the landmarks/parts for the face in box d.
        shape = predictor(img, d)

        # The various indices here are the predefined indices where the coordinates had been stored by the predictor.
        for i in range(36,42):
            leyeList.append([shape.part(i).x,shape.part(i).y])
        for i in range(42,48):
            reyeList.append([shape.part(i).x,shape.part(i).y])
        for i in range(48,60):
            mouthList.append([shape.part(i).x,shape.part(i).y])

    # Return the lists for left eye, right eye and mouth as a tuple of lists.
    return (leyeList,reyeList,mouthList)