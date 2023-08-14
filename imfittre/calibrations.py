# The Rb CSat values are computed from the K CSat values, assuming identical transmission through the optics and detection efficiencies. The vertical CSat has not been calibrated recently.
CSat = {
    "axial": {"K": 2970, "KRb": 2970, "Rb": 2882},
    "side": {"K": 2188, "KRb": 2188, "Rb": 2123},
    "vertical": {"K": 1400, "KRb": 1400, "Rb": 1359}
}

# Numerical aperture
NA = {
    "axial": 0.12,
    "side": 0.20,
    "vertical": 0.5
}

PX_SIZE = {
    "axial": 2.58,
    "side": 1.785,
    "vertical": 0.956
}

# Resonant cross section at I/Isat = 0, in um^2
SIGMA_0_K = 0.5*0.2807 # From Tiecke 40K data
SIGMA_0_Rb = 0.5*0.2907 # From Steck 87Rb data, table 7, assuming pi polarization
SIGMA_0 = {
    'K': SIGMA_0_K,
    'Rb': SIGMA_0_Rb,
    'KRb': SIGMA_0_K,
}

# Transfer efficiency
EFF_K = 1
EFF_Rb = 1
EFF_GSM = 0.82*0.7
EFF = {
    'K': EFF_K,
    'Rb': EFF_Rb,
    'KRb': EFF_GSM,
}

default_fit = {
    "|0,0>": {
        "species": "KRb",
        "bin": 1,
        "region": {
            "xc": 250,
            "yc": 340,
            "w": 85,
            "h": 35
        },
        "camera": "Side",
        "path": "side",
        "frames": {
            "shadow": 0,
            "light": 1,
            "dark": 2
        },
        "function": "Gaussian",
        "params": {
            "x0": [250, 210, 290],
            "y0": [340, 325, 355],
            "A": [1, 0, 5],
            "sigmax": [20, 1, 30],
            "sigmay": [5, 1, 30],
            "theta": 0,
            "offset": [0, -0.5, 0.5],
            "gradx": [0, -10, 10],
            "grady": [0, -10, 10]
        }
    },
    "|1,0>": {
        "species": "KRb",
        "bin": 1,
        "region": {
            "xc": 250,
            "yc": 340,
            "w": 85,
            "h": 35
        },
        "camera": "Side",
        "path": "side",
        "frames": {
            "shadow": 3,
            "light": 4,
            "dark": 5
        },
        "function": "Gaussian",
        "params": {
            "x0": [250, 210, 290],
            "y0": [340, 325, 355],
            "A": [1, 0, 5],
            "sigmax": [20, 1, 30],
            "sigmay": [5, 1, 30],
            "theta": 0,
            "offset": [0, -0.5, 0.5],
            "gradx": [0, -10, 10],
            "grady": [0, -10, 10]
        }
    }
}