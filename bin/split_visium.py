#!/usr/bin/env python3

"""
This code splits the Visium slide into four equal columns by dividing the slide width by the number of columns. 
It then crops each column region individually and saves them as separate SVS files named column_i.svs, where i represents the column index.
"""

__author__ = "Darwin D'Souza"
__version__ = "1.0.0"
__license__ = "MIT"


import openslide
from PIL import Image
import os
import argparse

def main(slide_path, shift_amount, image_list):
    # Open the Visium slide
    # slide_path = "3-11-2022_Visium_Slide1_Raphael.svs"
    slide = openslide.OpenSlide(slide_path)
    
    # Define the dimensions of the slide
    slide_width, slide_height = slide.dimensions
    
    # Define the number of columns for splitting
    num_columns = 4
    
    # Define the amount of shift (in pixels)
    # shift_amount = 5500  # Adjust this value as needed
    if shift_amount:
      shift_amount = int(shift_amount)
    else:
      shift_amount = 0  # Adjust this value as needed 
    
    # Recalculate slide width if shift exists
    slide_width = slide_width - (shift_amount*2)

    # Calculate the width of each column
    column_width = slide_width // num_columns
    # column_width = 17240

    #outdir = os.path.basename('3-11-2022_Visium_Slide1_Raphael.svs').split('.')[0]
    #os.makedirs(outdir, exist_ok=True)
    
    # Crop the slide into separate columns
    for i in range(num_columns):
#        if i==0:
#            x = 5300
#        elif i==1:
#            x = 23225
#        elif i==2:
#            x = 40830
#        elif i==3:
#            x = 58881
        
        x = (i * column_width) + shift_amount
        #y = 1600  # Starting from the top
        y = 0 # Adjust this value as needed

        # Read the column region as an image
        region = slide.read_region((x, y), 0, (column_width, slide_height-(y*2)))
    
        # Convert the image to RGB mode
        region_rgb = region.convert("RGB")
    
        # Save the column region image as a JPEG file
        #region_image_path = f"{outdir}/column_{i}.jpg"
        if image_list:
          region_image_path = f"{image_list[i]}.jpg"
        else:
          region_image_path = f"column_{i}.jpg"
        region_rgb.save(region_image_path, "JPEG")
    
    # Close the original slide
    slide.close()

if __name__ == '__main__':
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser()

    # Required positional argument
    parser.add_argument("slide_path", help="Visium full slide path")
    parser.add_argument('-s', '--shift', help="Shift length in pixels", required=False)
    parser.add_argument('-l','--image_names', nargs='+', help='Image names (left to right) eg. -l image1 image2 image3 image4', required=False)


    parser.add_argument(
    "--version",
    action="version",
    version="%(prog)s (version {version})".format(version=__version__))

    args = parser.parse_args()
    
    main(args.slide_path, args.shift, args.image_names)
