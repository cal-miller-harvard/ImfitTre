import numpy as np
from scipy.optimize import least_squares
from inspect import signature
from abc import ABC, abstractmethod
from skimage.feature import peak_local_max

from imfittre.helpers import image_process as ip

STATUS_DICT = {
    -1: "improper input parameters status returned from MINPACK",
    0: "the maximum number of function evaluations is exceeded",
    1: "gtol termination condition is satisfied",
    2: "ftol termination condition is satisfied",
    3: "xtol termination condition is satisfied",
    4: "both ftol and xtol termination conditions are satisfied",
}


class Fit(ABC):
    """Base class for fitting functions to data.

    Args:
        image (numpy.ndarray): The image to fit.
        data (dict): The image's metadata.
        config (dict): The config to use for fitting. Possible keys:
            "frame" (str): The frame to fit. Should be one of "OD", "shadow", "light", or "dark". Defaults to "OD".
            "region" (dict): The region to fit. If no region is given, the entire frame is fit. Should have keys:
                "xc" (int): The x coordinate of the center of the region.
                "yc" (int): The y coordinate of the center of the region.
                "w" (int): The width of the region.
                "h" (int): The height of the region.
            "fit_function" (str): The name of the function to fit. Defaults to "Gaussian".
            "params" (dict): The parameters to use for fitting. Each key should be the name of a parameter and each value should either be a number or a list. If a number is given, the parameter is fixed to that value. If a list is given, it should be of the form [initial value, lower bound, upper bound]. This key is required.
    """

    def __init__(self, image, data, config):
        self.image = image
        self.data = data
        self.config = config
        frame = config.get("frame", "OD")
        self.region = config.get("region", None)

        self.params = config.get("params", None)
        if self.params is None:
            raise ValueError("No parameters given for fit.")

        self.binning = self.data["binning"][0]

        if frame == "OD":
            self.frame = ip.calculateOD(self.image, self.data, self.config)
        else:
            self.frame = ip.crop_frame(
                self.image[self.config["frames"][frame]],
                self.config,
                binning=self.binning,
            )

        self.result = {}

    @abstractmethod
    def fit_function(self, x, y, **kwargs) -> np.ndarray:
        """The function to fit. Must be implemented in subclasses.

        Args:
            x (numpy.ndarray): The x values at which to evaluate the function.
            y (numpy.ndarray): The y values at which to evaluate the function.
            **kwargs: The parameters of the function.

        Returns:
            numpy.ndarray: The function evaluated at x and y.
        """
        pass

    def pre_process(self):
        """Pre-processing, including finding missing parameters."""
        region = self.config.get("region", None)
        peak = peak_local_max(self.frame, min_distance=15, num_peaks=1)
        if "x0" not in self.params and region is not None:
            self.params["x0"] = (
                peak[0][1],
                region["xc"] - region["w"] / 2,
                region["xc"] + region["w"] / 2,
            )
        if "y0" not in self.params and region is not None:
            self.params["y0"] = (
                peak[0][0],
                region["yc"] - region["h"] / 2,
                region["yc"] + region["h"] / 2,
            )

    @abstractmethod
    def post_process(self):
        """Post-processes the fit, calculating any necessary derived values. Must be implemented in subclasses."""
        pass

    def fit(self):

        p0 = []
        pmin = []
        pmax = []

        kwargs = {}
        posargs = {}

        function_params = signature(self.fit_function).parameters

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
        # in unbinned pixels
        if self.region is not None:
            x_offset = self.region["xc"] - self.region["w"] // 2
            y_offset = self.region["yc"] - self.region["h"] // 2
        else:
            x_offset = 0
            y_offset = 0

        # in unbinned pixels
        x = np.arange(self.frame.shape[1]) * self.binning + x_offset
        y = np.arange(self.frame.shape[0]) * self.binning + y_offset

        X, Y = np.meshgrid(x, y)

        def loss(params):
            for p in posargs:
                kwargs[p] = params[posargs[p]]
            return self.fit_function(X, Y, **kwargs).flatten() - self.frame.flatten()

        result = least_squares(loss, p0, bounds=(pmin, pmax))

        if result.status < 0:
            raise RuntimeError(STATUS_DICT[result.status])

        for p in posargs:
            kwargs[p] = result.x[posargs[p]]

        self.result = {"params": kwargs, "status": STATUS_DICT[result.status]}


from imfittre.fit import fit_functions as ff


def fit(image, data, config):
    """Fits a given image according to the given config.

    Args:
        image (numpy.ndarray): The image to fit.
        data (dict): The image's metadata.
        config (dict of dict): A dictionary of fits to apply to the image where the keys are the names of the fits and the values are the configs for the fits.

    Returns:
        dict: A dictionary of fits where the keys are the names of the fits and the values are the results of the fits.
    """
    fits = {}
    for name, fit_config in config.items():
        # if image is a dictionary, select the correct camera
        if isinstance(image, dict):
            im = image[fit_config["camera"]]
        else:
            im = image

        if fit_config["fit_function"] == "Gaussian":
            fit_class = ff.Gaussian
        elif fit_config["fit_function"] == "FermiDirac3D":
            fit_class = ff.FermiDirac3D
        else:
            print("Fit function {} not recognized.".format(fit_config["fit_function"]))

        f = fit_class(im, data["images"][fit_config["camera"]], fit_config)
        f.pre_process()
        f.fit()
        f.post_process()
        fits[name] = f.result
    return fits
