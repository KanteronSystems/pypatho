from skimage import io
from skimage.color import rgb2hed
from skimage.exposure import rescale_intensity

from PIL import Image

import matplotlib.pyplot as plt

import StringIO

# import os
# import opts


def processor(process, originalfile):
    # TODO Make a process number 'if' loop when we have different processes
    result = processhed(originalfile, process)
    return result


def processhed(imagefile, algorithm):
    image = plt.imread(StringIO.StringIO(imagefile), format="JPG")
 
    ihc_hed = rgb2hed(image)

    if algorithm == '01':
        result = plt.cm.gray(rescale_intensity(ihc_hed[:, :, 0], out_range=(0, 1)))
    elif algorithm == '02':
        result = plt.cm.gray(rescale_intensity(ihc_hed[:, :, 1], out_range=(0, 1)))
    elif algorithm == '03':
        result = plt.cm.gray(rescale_intensity(ihc_hed[:, :, 2], out_range=(0, 1)))
    else:
        result = image

    output = StringIO.StringIO()
    plt.imsave(output, result, format="PNG")
    contents = output.getvalue()
    output.close()

    return contents
