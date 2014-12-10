from skimage import io
from skimage.color import rgb2hed
from skimage.exposure import rescale_intensity

import matplotlib.pyplot as plt

# import os
# import opts


def processor(process, originalfile):
    target = io.imread(originalfile)
    # TODO Make a process number 'if' loop when we have different processes
    result = processhed(target, process)
    return result


def processhed(image, algorithm):
    # ihc_rgb = io.imread(file)
    # ihc_hed = rgb2hed(ihc_rgb)
    
    ihc_hed = rgb2hed(image)

    if algorithm == '01':
        result = plt.cm.gray(rescale_intensity(ihc_hed[:, :, 0], out_range=(0, 1)))
    elif algorithm == '02':
        result = plt.cm.gray(rescale_intensity(ihc_hed[:, :, 1], out_range=(0, 1)))
    elif algorithm == '03':
        result = plt.cm.gray(rescale_intensity(ihc_hed[:, :, 2], out_range=(0, 1)))
    else:
        result = image

    return result
