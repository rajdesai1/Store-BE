from PIL import Image
import matplotlib.pyplot as plt
import os
import datetime
import argparse
import torch
import random
import string
import numpy as np
from joblib import load
from sklearn.decomposition import PCA
from .measurement_evaluator import Human
from .utils.image_utils import ImgSizer
from .utils.model import *
from .utils.torchloader import *
import matplotlib.pyplot as plt
import trimesh
from Darwin.settings import MEDIA_ROOT

def main(front: np.ndarray,
         side: np.ndarray,
         gender: str,
         height: float,
         weight: float,
         feature_model='ae',
         mesh_name:str = 'subject.obj',
         measurement_model:str = 'calvis'):
    # parser = argparse.ArgumentParser()
    
    # parser.add_argument("--experiment", type=str, required = True, help='Give experiment name')
    # parser.add_argument("--front", type=str, required= True, help="path to front view image")
    # parser.add_argument("--side", type=str, required= True, help="path to side view image")
    # parser.add_argument("--gender", type=str, required = True)
    # parser.add_argument("--height", type=float, required = True)
    # parser.add_argument("--weight", type=float, required = True)
    # parser.add_argument("--feature_model", type=str, default='ae')
    # parser.add_argument("--mesh_name", type=str, default='subject.obj')
    # parser.add_argument("--measurement_model", type=str, default='calvis')

    # args = parser.parse_args()

    try:
        os.mkdir(os.path.join(f'{MEDIA_ROOT}/masks', 'demo'))
    except:
        pass
    
    # try:
    experiment = ''.join(random.choices(string.ascii_uppercase +string.digits, k=6)).lower()
    os.mkdir(os.path.join(f'{MEDIA_ROOT}/masks/demo', experiment))
    # except:
        # pass

    
    front = front/255.0
    side = side/255.0
    
    print("Data preprocessed! \n Extracting Important features")

    if feature_model == 'ae':
        
        feature_extractor_path = f'{MEDIA_ROOT}/weights/feature_extractor_{gender}_50.pth'
        feature_extractor_weights = torch.load(feature_extractor_path,  map_location=torch.device('cpu'))
        feature_extractor = Deep2DEncoder(image_size= 512 , kernel_size=3, n_filters=32)
        feature_extractor.load_state_dict(feature_extractor_weights)
        
        feature_extractor.eval()
        feature_extractor.requires_grad_(False)

        front = torch.tensor(front).float()
        side = torch.tensor(side).float()

        front_features = feature_extractor(front.view(1, 1, 512, 512)).detach().numpy().reshape(256)
        side_features = feature_extractor(side.view(1, 1, 512, 512)).detach().numpy().reshape(256)
        
        front_features = np.array(front_features)
        side_features = np.array(side_features)

        features = np.concatenate([front_features, side_features], axis = -1).reshape(1,512)
    
    if feature_model == 'pca':
        
        pca_front = load(f'{MEDIA_ROOT}/weights/pca_{gender}_front.joblib')
        pca_side = load(f'{MEDIA_ROOT}/weights/pca_{gender}_side.joblib')
        
        front_features = pca_front.transform(np.array(front).reshape(1, 512*512))
        side_features = pca_side.transform(np.array(side).reshape(1, 512*512))

        front_features = np.array(front_features)
        side_features = np.array(side_features)

        features = np.concatenate([front_features, side_features], axis = -1)
    print("Feature Extraction done \n Estimating Measurements")
    template = np.load(f'{MEDIA_ROOT}/data/{gender}_template.npy')
    shape_dirs = np.load(f'{MEDIA_ROOT}/data/{gender}_shapedirs.npy')
    faces =  np.load(f'{MEDIA_ROOT}/data/faces.npy')
    
    if measurement_model == 'nomo':
        features = np.concatenate([features, np.array(height).reshape(1,1)], axis = -1)
    else:
        features = np.concatenate([features, np.array(height).reshape(1,1), np.array(weight).reshape(1,1)], axis = -1)

    
    if measurement_model == 'nomo':
        human = load(f'{MEDIA_ROOT}/weights/nomo_{gender}_krr.pkl')
    
    else:
        human = load(f'{MEDIA_ROOT}/weights/calvis_{gender}_krr.pkl')
    
    features = np.array(features, dtype=float) 
    measurements = human.predict_measurements(features)
    shape = human.predict_shape(features)
    output_measurements = {}
    output_measurements['chest'] = measurements[0][0]
    output_measurements['hip'] = measurements[0][1]
    output_measurements['waist'] = measurements[0][2]

    print(f"Chest Circumference : {measurements[0][0]}")
    print(f"Hip Circumference : {measurements[0][1]}")
    print(f"Waist Circumference : {measurements[0][2]}")

    mesh = human.display_3D(shape)
    os.mkdir(os.path.join(f'{MEDIA_ROOT}/body_models/', experiment))
    mesh.export(os.path.join(f'{MEDIA_ROOT}/body_models/{experiment}',mesh_name))
    print("3D model saved!")

    return (output_measurements, os.path.join(f'{MEDIA_ROOT}/body_models/{experiment}',mesh_name))

# if __name__ == "__main__":
#     main()

   


    




    


    

    


    
