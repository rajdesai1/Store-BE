import os
    

import cv2
import torch
import numpy as np
import albumentations       # used for normalizing input images
from typing import Union       #for annotations
from pathlib import Path
from people_segmentation.pre_trained_models import create_model     #loading pretrained U-net model
#util(helper) functions for image processing
from iglovikov_helper_functions.utils.image_utils import load_rgb, pad, unpad
from iglovikov_helper_functions.dl.pytorch.utils import tensor_from_rgb_image



def img_segmenation(image: Union[Path, str]) -> np.ndarray:

        #load   ing image
        image = load_rgb(image)
        
        print(image)
        # loading UNet model
        model = create_model("Unet_2020-07-20")
        model.eval()    #running model in inference mode

        #intializing transformations from albumentations
        transform = albumentations.Compose([albumentations.Normalize(p=1)], p=1)
        
        padded_image, pads = pad(image, factor=32, border=cv2.BORDER_CONSTANT)  #giving padding to input image for U

        # apply
        x = transform(image=padded_image)["image"]
        x = torch.unsqueeze(tensor_from_rgb_image(x), 0)

        # used for not stop saving gradients
        with torch.no_grad():
            prediction = model(x)[0][0]

        
        mask = (prediction > 0).cpu().numpy().astype(np.uint8)      # creating mask of prediction
        mask = unpad(mask, pads)      # removing padding from mask(pads is parameters used to remove(undo padding applied on input image))

        # returning mask array
        return mask


    #     np.array_repr(image)

        
    #     cv2.imwrite('sbdf.jpg', mask)


    #     mask.shape





    #     image


    #     dst = cv2.addWeighted(image, 1, (cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB) * (0, 255, 0)).astype(np.uint8), 0.5, 0)


    #     cv2.imwrite('sdfsd.jpg', cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB) * (255, 255, 255)).astype(np.uint8)


    #     imshow(dst)





    # pass
