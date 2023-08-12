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
        "path": "side",
        "frames": {
            "shadow": 0,
            "light": 1,
            "dark": 2
        },
        "fit function": "gaussian"
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
        "path": "side",
        "frames": {
            "shadow": 3,
            "light": 4,
            "dark": 5
        },
        "fit function": "gaussian"
    }
}