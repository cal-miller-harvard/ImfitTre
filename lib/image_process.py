import numpy as np
import base64
from PIL import Image
from io import BytesIO

import calibrations

def crop_frame(frame, config):
    """Crops a frame according to the given config.

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
    xc = config["region"]["xc"]
    yc = config["region"]["yc"]
    w = config["region"]["w"]
    h = config["region"]["h"]
    return frame[yc-h//2:yc+h//2, xc-w//2:xc+w//2]

def calculateOD(image, config):
    shadow = image[config["frames"]["shadow"]]
    light = image[config["frames"]["light"]]
    dark = image[config["frames"]["dark"]]

    shadowCrop = crop_frame(shadow, config)
    lightCrop = crop_frame(light, config)
    darkCrop = crop_frame(dark, config)

    s1 = shadowCrop - darkCrop
    s2 = lightCrop - darkCrop
    OD = -np.log(s1/s2)

    species = config["species"]

    Ceff = calibrations.CSat[config['path']][species]
    bins = config["bin"]
    Ceff *= float(bins**2)

    ODCorrected = OD + (s2 - s1)/Ceff

    #Set all nans and infs to zero
    ODCorrected[np.isnan(ODCorrected)] = 0
    ODCorrected[np.isinf(ODCorrected)] = 0

    return ODCorrected

def np_to_html(image):
    rescaled = (255.0 / image.max() * (image - image.min())).astype(np.uint8)
    im = Image.fromarray(rescaled)
    with BytesIO() as output:
        im.save(output, format="PNG")
        contents = output.getvalue()
    encoded = base64.b64encode(contents).decode("utf-8")
    return "<img src='data:image/png;base64," + encoded + "'/>"