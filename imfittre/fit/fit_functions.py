import numpy as np
from imfittre.fit.image_fit import Fit
from scipy.special import spence
from mpmath import polylog


class Gaussian(Fit):
    def fit_function(
        self,
        x,
        y,
        x0=0.0,
        y0=0.0,
        A=0.0,
        sigmax=0.0,
        sigmay=0.0,
        theta=0.0,
        offset=0.0,
        gradx=0.0,
        grady=0.0,
    ):
        """A 2D Gaussian function with a linear background.

        Args:
            x (numpy.ndarray): The x values at which to evaluate the function.
            y (numpy.ndarray): The y values at which to evaluate the function.
            x0 (float): The x coordinate of the center of the Gaussian.
            y0 (float): The y coordinate of the center of the Gaussian.
            A (float): The amplitude of the Gaussian.
            sigmax (float): The standard deviation of the Gaussian in the x direction.
            sigmay (float): The standard deviation of the Gaussian in the y direction.
            theta (float): The angle of the Gaussian in radians.
            offset (float): The offset of the linear background.
            gradx (float): The gradient of the linear background in the x direction.
            grady (float): The gradient of the linear background in the y direction.

        Returns:
            numpy.ndarray: The function evaluated at x and y.
        """
        x = np.array(x)
        y = np.array(y)
        x = x - x0
        y = y - y0
        xprime = x * np.cos(theta) - y * np.sin(theta)
        yprime = x * np.sin(theta) + y * np.cos(theta)
        return (
            A * np.exp(-0.5 * (xprime**2 / sigmax**2 + yprime**2 / sigmay**2))
            + offset
            + gradx * x
            + grady * y
        )

    def post_process(self):
        res = self.result.get("params", {})

        px_size = self.config["calibrations"]["px_size_um"]
        eff = self.config["calibrations"]["eff"]
        lmda = self.config["calibrations"]["lambda_m"]

        derived = {}
        derived["sigmax_um"] = res["sigmax"] * px_size
        derived["sigmay_um"] = res["sigmay"] * px_size
        derived["N"] = (
            (1 / eff)
            * 2
            * res["A"]
            * (1e-6) ** 2
            * derived["sigmax_um"]
            * derived["sigmay_um"]
            * (2 * np.pi) ** 2
            / (3 * lmda**2)
        )

        self.result["derived"] = derived


class FermiDirac3D(Fit):
    def fit_function(
        self,
        x,
        y,
        x0=0.0,
        y0=0.0,
        A=0.0,
        q=0.0,
        sigmax=0.0,
        sigmay=0.0,
        theta=0.0,
        offset=0.0,
        gradx=0.0,
        grady=0.0,
    ):
        """A 3D Fermi-Dirac distribution with a linear background. See https://arxiv.org/pdf/0801.2500

        Args:
            x (numpy.ndarray): The x values at which to evaluate the function.
            y (numpy.ndarray): The y values at which to evaluate the function.
            x0 (float): The x coordinate of the center of the distribution.
            y0 (float): The y coordinate of the center of the distribution.
            A (float): The peak OD of the distribution.
            q (float): The logarithm of the fugacity of the gas (q = \mu \beta).
            sigmax (float): The standard deviation of the distribution in the x direction.
            sigmay (float): The standard deviation of the distribution in the y direction.
            theta (float): The angle of the distribution in radians.
            offset (float): The offset of the linear background.
            gradx (float): The gradient of the linear background in the x direction.
            grady (float): The gradient of the linear background in the y direction.

        Returns:
            numpy.ndarray: The function evaluated at x and y.
        """
        x = np.array(x)
        y = np.array(y)
        x = x - x0
        y = y - y0
        xprime = x * np.cos(theta) - y * np.sin(theta)
        yprime = x * np.sin(theta) + y * np.cos(theta)

        def f(x):
            return (1 + x) * np.log(1 + x) / x

        def Li2(x):
            return spence(1 - x)

        return (
            A
            * Li2(
                -np.exp(
                    q
                    - 0.5
                    * (xprime**2 / sigmax**2 + yprime**2 / sigmay**2)
                    * f(np.exp(q))
                )
            )
            / Li2(-np.exp(q))
            + offset
            + gradx * x
            + grady * y
        )

    def pre_process(self):
        pass

    def post_process(self):
        res = self.result["params"]

        px_size = self.config["calibrations"]["px_size_um"]
        eff = self.config["calibrations"]["eff"]
        lmda = self.config["calibrations"]["lambda_m"]

        derived = {}
        derived["ToverTF"] = (-6 * float(polylog(3, -np.exp(res["q"])))) ** (-1 / 3)
        derived["sigmax_um"] = res["sigmax"] * px_size  # check this!
        derived["sigmay_um"] = res["sigmay"] * px_size  # check this!
        derived["N"] = (
            (1 / eff)
            * (1e-6) ** 2  # micron to meter
            / (3 * lmda**2 / (2 * np.pi))  # scattering cross section
            * np.pi
            * res["A"]
            * (2 * derived["sigmax_um"])
            * (2 * derived["sigmay_um"])
            * float(polylog(3, -np.exp(res["q"])))
            * float(polylog(0, -np.exp(res["q"])))
            / float(polylog(2, -np.exp(res["q"])))
            / float(polylog(1, -np.exp(res["q"])))
        )

        self.result["derived"] = derived
