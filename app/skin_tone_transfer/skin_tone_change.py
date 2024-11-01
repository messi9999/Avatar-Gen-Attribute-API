from .skin.skinDetection import change_skin
from .skin.noFaceSkinDetection import obtain_skin_color
import cv2
import numpy as np

import logging

def execute(which, img, col, res):
    try:
        with open(img, 'rb') as inputImage:
            if which == "color":
                result = change_skin(inputImage, col)
            elif which == "image":
                color = obtain_skin_color(col)
                color = np.uint8([[color]])
                color = cv2.cvtColor(color, cv2.COLOR_HSV2RGB)
                color = color[0][0]
                result = change_skin(inputImage, color, res)
            else:
                raise ValueError("Please enter correct detection type.")

        with open(res, 'wb') as resultFile:
            resultFile.write(result)

        return res

    except Exception as e:
        logging.error(f"An error occurred to execute skin tone change: {e}")
        raise  # Re-raise the caught exception to handle it further up the call stack