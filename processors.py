# from skimage import data,io
from skimage.color import rgb2hed
from skimage.exposure import rescale_intensity

import matplotlib.pyplot as plt

# import os
# import opts


def processhed(image, algorithm):
    # ihc_rgb = io.imread(file)
    # ihc_hed = rgb2hed(ihc_rgb)
    
    ihc_hed = rgb2hed(image)

    if algorithm == 1:
        result = plt.cm.gray(rescale_intensity(ihc_hed[:, :, 0], out_range=(0, 1)))
    elif algorithm == 2:    
        result = plt.cm.gray(rescale_intensity(ihc_hed[:, :, 1], out_range=(0, 1)))
    elif algorithm == 3:
        result = plt.cm.gray(rescale_intensity(ihc_hed[:, :, 2], out_range=(0, 1)))
    else:
        result = image

    return result
