#!/usr/bin/env python
# coding: utf-8

"""
Segment Visium jpeg file using stardist and coordinates from Space Ranger
"""

__author__ = "Darwin D'Souza"
__version__ = "1.0.0"
__license__ = "MIT"


import numpy as np

# Import squidpy and additional packages needed for this tutorial.
import squidpy as sq

# Import the recommended normalization technique for stardist.
from csbdeep.utils import normalize

# Import the StarDist 2D segmentation models.
from stardist.models import StarDist2D

import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
import json
from multiprocessing import Pool
import time
import tempfile
import shutil
import random
import argparse
import os

def stardist_2D_versatile_he(img, nms_thresh=None, prob_thresh=None):
#     axis_norm = (0,1)   # normalize channels independently
    axis_norm = (0, 1, 2)  # normalize channels jointly
    # Make sure to normalize the input image beforehand or supply a normalizer to the prediction function.
    # this is the default normalizer noted in StarDist examples.
    img = normalize(img, 1, 99, axis=axis_norm)
    
#     model = StarDist2D.from_pretrained("2D_versatile_he")

#     temp_dir = tempfile.TemporaryDirectory()
#     print('created temporary directory', temp_dir.name)
#     destination = shutil.copytree('models', f'{temp_dir.name}/stardist', dirs_exist_ok=True)
#     model = StarDist2D(config=None,name='stardist', basedir=temp_dir.name)
    
    model = StarDist2D(config=None,name='python_2D_versatile_he',
        basedir='/sc/arion/projects/HIMC/nextflow/visium_segmentation/bin/models')

    labels, _ = model.predict_instances(
        img, nms_thresh=nms_thresh, prob_thresh=prob_thresh
    )
#     temp_dir.cleanup()
    return labels

def segment_bc(bc,x,y,rad):
   
    try:
      crop_center = img.crop_center(x, y, radius=int(spot_radius_fullres))
    except ValueError as e:
      print(e)
      return np.nan
    
    sq.im.segment(
    img=crop_center,
    layer="image",
    channel=None,
    method=stardist_2D_versatile_he,
    layer_added="segmented_stardist_default",
    prob_thresh=0.3,
    nms_thresh=None,
    )

    print(
        f"Number of segments in crop: {len(np.unique(crop_center['segmented_stardist_default']))}"
    )
    
    fig, axes = plt.subplots(1, 2)
    crop_center.show("image", ax=axes[0])
    _ = axes[0].set_title("H&H")
    crop_center.show("segmented_stardist_default", cmap="jet", interpolation="none", ax=axes[1])
    _ = axes[1].set_title("segmentation")
    plt.savefig(f'plots/{bc}.png')
    
    # double check -1 below
#     temp_dir.cleanup()

    return len(np.unique(crop_center['segmented_stardist_default']))-1

def main(jpeg, scalefactors, positions):
    
    source_image_path=jpeg
    Image.MAX_IMAGE_PIXELS=None
    im = Image.open(source_image_path)
    image_hires = np.array(im)

    # remove extra channel if it exists
    image_hires = image_hires[:, :, :3].copy()
    
    global img
    img = sq.im.ImageContainer(image_hires)


    df_pos = pd.read_csv(positions,
                         index_col=0, header=None,
                         names=['in_tissue','row','col','cx','cy'])

    # if cytassist, header already present..drop it
    if df_pos.iloc[0].name == 'barcode':
      df_pos = df_pos.drop(['barcode']) 


    with open(scalefactors, 'r') as f:
        scale_factors = json.load(f)
#     print(scale_factors)
    
    global spot_diameter_fullres
    global spot_radius_fullres
    spot_diameter_fullres = scale_factors['spot_diameter_fullres']
    spot_radius_fullres = spot_diameter_fullres//2
    
    # filter for spots in tissue
    df_pos_in = df_pos[df_pos['in_tissue']==1]
#     df_pos_in = df_pos_in.iloc[:100]
#
    os.makedirs('plots', exist_ok=True)
    
    start = time.time()
    with Pool(5) as p:
        detections = p.starmap(segment_bc,
                               zip(
                                   df_pos_in.index.tolist(),
                                   df_pos_in['cx'].values.tolist(),
                                   df_pos_in['cy'].values.tolist(),
                                   [spot_radius_fullres for i in range(df_pos_in.shape[0])]
                               ))
        detections_dict = dict(zip(df_pos_in.index.tolist(), detections))
    
#     start = time.time()
#     detections_dict = {}
#     for i in range(df_pos_in.shape[0]):
#         out = segment_bc(df_pos_in.iloc[i]['cx'],
#                    df_pos_in.iloc[i]['cy'],
#                    spot_radius_fullres)

#         bc = df_pos_in.iloc[i].name
#         detections_dict[bc] = out
        
    detections_df = pd.DataFrame.from_dict(
        detections_dict,orient='index',columns=['Stardist detections']).to_csv('stardist_detections.csv')
    print(time.time() - start)
    


if __name__=='__main__':
    
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser()

    # Required positional argument
    parser.add_argument("jpeg", help="Visium JPEG file")
    parser.add_argument("scalefactors", help="image_scalefactors.json or scalefactors.json from Space Ranger")
    parser.add_argument("positions", help="tissue_positions_list.csv from Space Ranger")

    parser.add_argument(
    "--version",
    action="version",
    version="%(prog)s (version {version})".format(version=__version__))

    args = parser.parse_args()

    main(args.jpeg, args.scalefactors, args.positions)
    


# TEST
# source_image_path="column_0.jpg"
# '/sc/arion/projects/HIMC/software/spaceranger_imaging/test2/outs/tissue_positions_list.csv'
# '/sc/arion/projects/HIMC/software/spaceranger_imaging/test2/outs/image_scalefactors.json'
