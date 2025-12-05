"""Market parameters like MSP, historical medians etc. For simulation we assume values and keep grade hierarchy."""

# MSP per crop per quintal (Rs/quintal)
MSP = {
    'Potato': 3000,  # Rs/quintal => Rs30/kg
    'Onion': 1500,
    'Tomato': 2500
}

# For simplicity, hist median and recent median per (crop, grade)
# We ensure Super > A > B > C by grade premiums
GRADE_PREM = {'Super':1.15, 'A':1.05, 'B':1.0, 'C':0.9}

BASE_HIST_MEDIAN = {'Potato':3200, 'Onion':1800, 'Tomato':2700}
BASE_RECENT = {'Potato':3100, 'Onion':1700, 'Tomato':2600}

# volatility (std dev) per crop
VOLATILITY = {'Potato':150, 'Onion':200, 'Tomato':180}  # Rs/quintal

# weights
W1, W2, W3 = 0.2, 0.5, 0.3
K_BAND = 2
DAILY_CAP_PCT = 0.20


def get_hist_median(crop, grade):
    return BASE_HIST_MEDIAN[crop] * GRADE_PREM[grade]

def get_recent_median(crop, grade):
    return BASE_RECENT[crop] * GRADE_PREM[grade]


def get_msp(crop):
    return MSP[crop]


def get_volatility(crop):
    return VOLATILITY[crop]


