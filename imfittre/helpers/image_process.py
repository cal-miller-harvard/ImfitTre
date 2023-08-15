import numpy as np
from scipy.optimize import least_squares
from matplotlib import pyplot as plt
from io import BytesIO

def crop_frame(frame, config):
    """Crops a frame according to the given config. If no region is given, the entire frame is returned.

    Args:
        frame (numpy.ndarray): The frame to crop.
        config (dict): The config to use for cropping. Should have a dictionary with key "region" the following keys:
            xc (int): The x coordinate of the center of the crop.
            yc (int): The y coordinate of the center of the crop.
            w (int): The width of the crop.
            h (int): The height of the crop.

    Returns:
        numpy.ndarray: The cropped frame.
    """
    if "region" not in config:
        return frame
    
    xc = config["region"]["xc"]
    yc = config["region"]["yc"]
    w = config["region"]["w"]
    h = config["region"]["h"]

    xmin = max(0, xc-w//2)
    xmax = min(frame.shape[1], xc+w//2)
    ymin = max(0, yc-h//2)
    ymax = min(frame.shape[0], yc+h//2)

    return frame[ymin:ymax, xmin:xmax]

def calculateOD(image, metadata, config):
    shadow = image[config["frames"]["shadow"]]
    light = image[config["frames"]["light"]]
    dark = image[config["frames"]["dark"]]
    Ceff = config["calibrations"]["csat"]

    # Note that this will only work for equal x and y binning
    bins = metadata["binning"][0] 

    shadowCrop = crop_frame(shadow, config)
    lightCrop = crop_frame(light, config)
    darkCrop = crop_frame(dark, config)

    s1 = shadowCrop - darkCrop
    s2 = lightCrop - darkCrop
    OD = -np.log(s1/s2)

    Ceff *= bins**2

    ODCorrected = OD + (s2 - s1)/Ceff

    #Set all nans and infs to zero
    ODCorrected[np.isnan(ODCorrected)] = 0
    ODCorrected[np.isinf(ODCorrected)] = 0

    return ODCorrected

def array_to_png(image, max_val=None, min_val=None, cmap="inferno"):
    """Converts a numpy array to an HTML image tag.

    Args:
        image (numpy.ndarray): The image to convert.
        max_val (float, optional): The maximum value of the image. Pixels greater than max_val will be clipped. Defaults to None, in which case the maximum value of the image is used.
        min_val (float, optional): The minimum value of the image. Pixels less than min_val will be clipped. Defaults to None, in which case the minimum value of the image is used.
        cmap (str, optional): The matplotlib colormap to use. Defaults to "inferno".

    Returns:
        str: The HTML image tag.
    """
    if max_val is None:
        max_val = image.max()
    if min_val is None:
        min_val = image.min()
    output = BytesIO()
    plt.imsave(output, image, cmap=cmap, vmin=min_val, vmax=max_val, format='png')
    output.seek(0)
    return output