"""Generate farmers, buyers and static market params"""
import pandas as pd
import numpy as np
from .utils import make_id, RNG

# Crop varieties mapping
CROPS = {
    'Potato': ['Kufri Badshah', 'Kufri Sindhuri'],
    'Onion': ['Light Red', 'Pusa Red', 'Pusa White Flat'],
    'Tomato': ['Vaishali', 'Anup', 'Arka Vishal']
}

# Yields (quintal / hectare) - assumed from public stats (see README or citations)
YIELDS_Q_PER_HA = {
    'Potato': 242.5,   # quintal/ha
    'Onion': 275.0,
    'Tomato': 245.6
}

def generate_farmers(n=100):
    """Generate farmer population with areas and cropping"""
    farmers = []
    # composition
    counts = {
        'marginal': int(0.55*n),
        'small': int(0.30*n),
        'medium': int(0.10*n),
        'large': n - (int(0.55*n)+int(0.30*n)+int(0.10*n))
    }
    def sample_area(cat):
        if cat=='marginal':
            return RNG.uniform(0.5,1.0)
        if cat=='small':
            return RNG.uniform(1.0,2.0)
        if cat=='medium':
            return RNG.uniform(2.0,10.0)
        return RNG.uniform(10.0,15.0)

    geohash_stub = ['7m0','7m1','7m2','7m3','7m4']
    fid = 1
    for cat, cnt in counts.items():
        for _ in range(cnt):
            area = round(sample_area(cat),3)
            crop = RNG.choice(list(CROPS.keys()))
            variety = RNG.choice(CROPS[crop])
            # quantity produced in quintal = yield * area
            qty = float(round(YIELDS_Q_PER_HA[crop] * area,2))
            farmers.append({
                'farmer_id': make_id('F'),
                'area_ha': area,
                'category': cat,
                'crop': crop,
                'variety': variety,
                'quantity_q': qty,
                'geohash': RNG.choice(geohash_stub)
            })
            fid += 1
    return pd.DataFrame(farmers)


def generate_buyers(m=120):
    buyers = []
    for _ in range(m):
        crop = RNG.choice(list(CROPS.keys()))
        variety = RNG.choice(CROPS[crop])
        grade = RNG.choice(['Super','A','B','C'])
        qty = round(RNG.uniform(5,200),2)  # quintal
        # bid price: we'll assume a base price range per crop
        base = {
            'Potato': 3000, # Rs/quintal ~ Rs30/kg
            'Onion': 2000,
            'Tomato': 3000
        }[crop]
        # bids around base with dispersion
        bid = round(RNG.gauss(base*1.0, base*0.15))
        buyers.append({'buyer_id': make_id('B'), 'crop': crop, 'variety': variety, 'grade': grade, 'quantity_q': qty, 'bid': max(0, bid)})
    return pd.DataFrame(buyers)
