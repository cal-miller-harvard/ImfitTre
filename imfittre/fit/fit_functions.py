import numpy as np

def Gauss2D(x, y, x0=0, y0=0, A=0, sigmax=0, sigmay=0, theta=0, offset=0, gradx=0, grady=0):
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
    xprime = x*np.cos(theta) - y*np.sin(theta)
    yprime = x*np.sin(theta) + y*np.cos(theta)
    return A*np.exp(-0.5*(xprime**2/sigmax**2 + yprime**2/sigmay**2)) + offset + gradx*x + grady*y
