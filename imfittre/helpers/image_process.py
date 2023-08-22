import numpy as np
from scipy.optimize import least_squares
from matplotlib import pyplot as plt
from io import BytesIO
from PIL import Image, ImageDraw

def crop_frame(frame, config, binning=1):
    """Crops a frame according to the given config. If no region is given, the entire frame is returned.

    Args:
        frame (numpy.ndarray): The frame to crop.
        config (dict): The config to use for cropping. Should have a dictionary with key "region" the following keys:
            xc (int): The x coordinate of the center of the crop.
            yc (int): The y coordinate of the center of the crop.
            w (int): The width of the crop.
            h (int): The height of the crop.
        binning (int, optional): The bin size of the frame. Defaults to 1.

    Returns:
        numpy.ndarray: The cropped frame.
    """
    if "region" not in config:
        return frame
    
    xc = config["region"]["xc"] // binning
    yc = config["region"]["yc"] // binning
    w = config["region"]["w"] // binning
    h = config["region"]["h"] // binning

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

    shadowCrop = crop_frame(shadow, config, bins)
    lightCrop = crop_frame(light, config, bins)
    darkCrop = crop_frame(dark, config, bins)

    s1 = shadowCrop - darkCrop
    s2 = lightCrop - darkCrop
    OD = -np.log(s1/s2)

    Ceff *= bins**2

    ODCorrected = OD + (s2 - s1)/Ceff

    #Set all nans and infs to zero
    ODCorrected[np.isnan(ODCorrected)] = 0
    ODCorrected[np.isinf(ODCorrected)] = 0

    return ODCorrected

from PIL import Image

def array_to_png(image, max_val=None, min_val=None, cmap="inferno", width=None, height=None):
    """Converts a numpy array to an HTML image tag.

    Args:
        image (numpy.ndarray): The image to convert.
        max_val (float, optional): The maximum value of the image. Pixels greater than max_val will be clipped. Defaults to None, in which case the maximum value of the image is used.
        min_val (float, optional): The minimum value of the image. Pixels less than min_val will be clipped. Defaults to None, in which case the minimum value of the image is used.
        cmap (str, optional): The matplotlib colormap to use. Defaults to "inferno".
        width (int, optional): The width of the output image. Defaults to None.
        height (int, optional): The height of the output image. Defaults to None.

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

    img = Image.open(output)
    if width is not None and height is not None:
        img = img.resize((width, height), resample=Image.NEAREST)
    elif width is not None:
        img = img.resize((width, img.height * width // img.width), resample=Image.NEAREST)
    elif height is not None:
        img = img.resize((img.width * height // img.height, height), resample=Image.NEAREST)
    output = BytesIO()
    img.save(output, format='png')
    output.seek(0)

    return output

def fit_to_image(fit, background=None, color="green", thickness=1):
    """Draws an image overlay with the given fit parameters.

    Draws a crosshair at params.x0, params.y0 with width params.sigmax, height params.sigmay and angle theta. The background is transparent.

    The size of the image is given by config.region.w and config.region.h. The center of the image is given by config.region.xc and config.region.yc.

    Args:
        fit (dict): The fit parameters.
        background (BytesIO, optional): A BytesIO object containing the background image. If None, a blank image is used. Defaults to None.
        color (str, optional): The color of the crosshair. Defaults to "white".
    """

    # Get the region information
    xc = fit["config"]["region"]["xc"]
    yc = fit["config"]["region"]["yc"]
    w = fit["config"]["region"]["w"]
    h = fit["config"]["region"]["h"]

    if background is None:
        # Create a transparent image with the same size as the crop region
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    else:
        # Load the background image
        background.seek(0)
        img = Image.open(background)

    # Extract the fit parameters 
    scale_factor = img.width / w
    x0 = (fit["result"]["params"]["x0"] - xc + w//2) * scale_factor
    y0 = (fit["result"]["params"]["y0"] - yc + h//2) * scale_factor
    sigmax = fit["result"]["params"]["sigmax"] * scale_factor
    sigmay = fit["result"]["params"]["sigmay"] * scale_factor
    theta = fit["result"]["params"]["theta"]

    # Draw the crosshair
    draw = ImageDraw.Draw(img)
    draw.line((x0-sigmax*np.cos(theta), y0-sigmax*np.sin(theta), x0+sigmax*np.cos(theta), y0+sigmax*np.sin(theta)), fill=color, width=int(thickness))
    draw.line((x0-sigmay*np.sin(theta), y0+sigmay*np.cos(theta), x0+sigmay*np.sin(theta), y0-sigmay*np.cos(theta)), fill=color, width=int(thickness))

    # Convert the image to a png
    output = BytesIO()
    img.save(output, format='png')
    output.seek(0)

    return output