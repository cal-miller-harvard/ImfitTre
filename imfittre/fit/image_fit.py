import numpy as np
from scipy.optimize import least_squares
from inspect import signature
from functools import partial

from imfittre.fit import fit_functions as ff
from imfittre.helpers import image_process as ip

STATUS_DICT = {
    -1: "improper input parameters status returned from MINPACK",
    0: "the maximum number of function evaluations is exceeded",
    1: "gtol termination condition is satisfied",
    2: "ftol termination condition is satisfied",
    3: "xtol termination condition is satisfied",
    4: "both ftol and xtol termination conditions are satisfied",
}

class Fit:
    """Base class for fitting functions to data.
    
    Args:
        config (dict): The config to use for fitting. Possible keys:
            "frame" (str): The frame to fit. Should be one of "OD", "shadow", "light", or "dark". Defaults to "OD".
            "region" (dict): The region to fit. If no region is given, the entire frame is fit. Should have keys:
                "xc" (int): The x coordinate of the center of the region.
                "yc" (int): The y coordinate of the center of the region.
                "w" (int): The width of the region.
                "h" (int): The height of the region.
            "function" (str): The name of the function to fit. Defaults to "Gaussian".
            "params" (dict): The parameters to use for fitting. Each key should be the name of a parameter and each value should either be a number or a list. If a number is given, the parameter is fixed to that value. If a list is given, it should be of the form [initial value, lower bound, upper bound]. This key is required.
    """
    def __init__(self, config):
        self.config = config
        self.frame = config.get("frame", "OD")
        self.region = config.get("region", None)

        function_name = config.get("function", "Gaussian")
        if function_name == "Gaussian":
            self.function = ff.Gauss2D
        else:
            raise ValueError("Invalid function name.")

        self.params = config.get("params", None)
        if self.params is None:
            raise ValueError("No parameters given for fit.")


    def fit(self, image):
        if self.frame == "OD":
            frame = ip.calculateOD(image, self.config)
        else:
            frame = ip.crop_frame(image[self.config["frames"][self.frame]], self.config)

        p0 = []
        pmin = []
        pmax = []

        kwargs = {}
        posargs = {}

        function_params = signature(self.function).parameters

        arg_idx = 0
        for p in function_params:
            # x and y are the coordinates at which the function is evaluated
            if p == "x" or p == "y":
                continue
            if p not in self.params:
                raise ValueError("Parameter {} not given.".format(p))
            
            if isinstance(self.params[p], list):
                p0.append(self.params[p][0])
                pmin.append(self.params[p][1])
                pmax.append(self.params[p][2])
                posargs[p] = arg_idx
                arg_idx += 1
            else:
                kwargs[p] = self.params[p]

        # offset X and Y relative to the corner of the region
        if self.region is not None:
            x_offset = self.region["xc"] - self.region["w"]//2
            y_offset = self.region["yc"] - self.region["h"]//2

        x = np.arange(frame.shape[1]) + x_offset
        y = np.arange(frame.shape[0]) + y_offset

        X, Y = np.meshgrid(x, y)

        def loss(params):
            for p in posargs:
                kwargs[p] = params[posargs[p]]
            return self.function(X, Y, **kwargs).flatten() - frame.flatten()
        
        result = least_squares(loss, p0, bounds=(pmin, pmax))
        return result


def fit(image, config):
    """Fits a given image according to the given config.

    Args:
        image (numpy.ndarray): The image to fit.
        config (dict of dict): A dictionary of fits to apply to the image where the keys are the names of the fits and the values are the configs for the fits.

    Returns:
        dict: A dictionary of fits where the keys are the names of the fits and the values are the results of the fits.
    """
    fits = {}
    for name, fit_config in config.items():
        # if image is a dictionary, select the correct camera
        if isinstance(image, dict):
            fits[name] = Fit(fit_config).fit(image[fit_config["camera"]])
        else:
            fits[name] = Fit(fit_config).fit(image)
    return fits