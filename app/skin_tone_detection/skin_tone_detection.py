import stone
from json import dumps
import time
import json
from urllib.parse import urlparse, unquote

import stone.image


image_type="auto"
# palette=["#373028", "#422811", "#513b2e", "#6f503c", "#81654f", "#9d7a54", "#bea07e", "#e5c8a6", "#e7c1b8", "#f3dad6", "#fbf2f3"]
# label=["CA", "CB", "CC", "CD", "CE", "CF", "CG", "CH", "CI", "CJ", "CK"]
other_args = []

def load_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


def detect_skin_tone(image_path, color_type):
    
    palette_obj = load_json_file(file_path="app/palette.json")
    

    if palette_obj[color_type] == {} or palette_obj[color_type] == None:
        return {}
    
    palette = []
    label = []
    group_name = []
    

    for group in palette_obj[color_type]:
        # print(palette_obj[color_type][group])
        group_obj = palette_obj[color_type][group]
        
        group_colors = list(group_obj.values())
        group_labels = list(group_obj.keys())
        
        group_n = [group] * len(group_labels)
        
        palette = palette + group_colors
        label = label + group_labels
        group_name = group_name + group_n

    time_time = time.time()
    
    result = stone.process(
        filename_or_url=image_path,
        image_type=image_type,
        tone_palette=palette,
        tone_labels=label, *other_args, return_report_image=True)
    print("inference time: {} s".format(round(time.time() - time_time, 4)))
    
    # show the report image
    report_images = result.pop("report_images")  # obtain and remove the report image from the `result`
    face_id = 1
    # stone.show(report_images[face_id])

    # convert the result to json
    result_json = dumps(result)

    parsed_result = json.loads(result_json)
    
    dominant_color = parsed_result["faces"][0]["dominant_colors"][0]
    skin_tone = parsed_result["faces"][0]["skin_tone"]
    color_label = parsed_result["faces"][0]['tone_label']
    which_group = group_name[label.index(color_label)]
    
    result = {
        "dominant_color": dominant_color,
        "skin_tone": skin_tone,
        "color_label": color_label,
        "which_group": which_group
    }

    # return parsed_result["faces"][0]["skin_tone"]
    return result