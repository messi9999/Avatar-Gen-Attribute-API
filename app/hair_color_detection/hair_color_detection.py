from .hair_color_detector import HairColorDetector
import numpy as np

hcd = HairColorDetector()

def detect_hair_color(image_path):
    hair_segment, hair_mask, dominant_color = hcd.get_color(image_path,  save_result=False)
    
    print(type(dominant_color))
    print(dominant_color)
    
    return np.array(dominant_color).tolist()
    
    