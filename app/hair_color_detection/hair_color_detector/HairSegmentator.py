import torch
from .model import BiSeNet
import numpy as np
from PIL import Image
import torchvision.transforms as transforms
import cv2
import os
import requests

class HairSegmentator():
  
    def __init__(self):
        self.anno = None
        n_classes = 19
        self.net = BiSeNet(n_classes=n_classes)
        PATH = get_model_file()
        self.net.load_state_dict(torch.load(PATH, map_location=torch.device('cpu')))
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.net.to(device)
        self.net.eval()
        self.to_tensor = transforms.Compose([
              transforms.ToTensor(),
              transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
          ])

    def vis_parsing_maps(self,im, parsing_anno, stride, save_im=False, save_path='vis_results/parsing_map_on_im.jpg'):
        # Colors for all 20 parts
        part_colors = [[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],
                      [0,0,0], [0,0,0], [0,0,0], [0,0,0], [0,0,0],
                      [255, 255, 255],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]

        im = np.array(im)
        vis_im = im.copy().astype(np.uint8)
        vis_parsing_anno = parsing_anno.copy().astype(np.uint8)
        vis_parsing_anno = cv2.resize(vis_parsing_anno, None, fx=stride, fy=stride, interpolation=cv2.INTER_NEAREST)
        vis_parsing_anno_color = np.zeros((vis_parsing_anno.shape[0], vis_parsing_anno.shape[1], 3)) + 255

        num_of_class = np.max(vis_parsing_anno)

        for pi in range(1, num_of_class + 1):
            index = np.where(vis_parsing_anno == pi)
            vis_parsing_anno_color[index[0], index[1], :] = part_colors[pi]

        vis_parsing_anno_color = vis_parsing_anno_color.astype(np.uint8)
        # print(vis_parsing_anno_color.shape, vis_im.shape)
        vis_im = cv2.addWeighted(cv2.cvtColor(vis_im, cv2.COLOR_RGB2BGR), 0.4, vis_parsing_anno_color, 0.6, 0)
        self.anno = vis_parsing_anno
        # Save result or not
          # if save_im:
          #     cv2.imwrite("parsing"+'.png', vis_parsing_anno)
          #     cv2.imwrite("parsing"+".jpg", vis_im, [cv2.IMWRITE_JPEG_QUALITY, 100])

    def get_parsing(self,img,save_path="/content"):
        
        # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        with torch.no_grad():
            # img = Image.open(img_path)
            img = Image.fromarray(img)
            image = img.resize((512, 512), Image.BILINEAR)
            img = self.to_tensor(image)
            img = torch.unsqueeze(img, 0)
            if torch.cuda.is_available():
                img = img.cuda()

            out = self.net(img)[0]
            parsing = out.squeeze(0).cpu().numpy().argmax(0)
            self.vis_parsing_maps(image, parsing, stride=1, save_im=True, save_path=save_path)
            return parsing
      

    def hair(self, parsing, part=17):
        return np.expand_dims(np.array(parsing == part).astype('uint8'), axis=-1) * 255

import pkg_resources


args_79999_iter_path = "./79999_iter.pth"

model_url = "https://raw.githubusercontent.com/zllrunning/face-makeup.PyTorch/blob/master/cp/79999_iter.pth"

def get_model_file():
    if not os.path.exists(args_79999_iter_path):
        # Send a GET request to the URL
        response = requests.get(model_url, stream=True)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Write the file contents to the local file
            with open(args_79999_iter_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"File downloaded successfully: {args_79999_iter_path}")
        else:
            print(f"Failed to download file. Status code: {response.status_code}")
    else:
        print(f"File already exists: {args_79999_iter_path}")
    path = pkg_resources.resource_filename(__name__, '79999_iter.pth')
    return path