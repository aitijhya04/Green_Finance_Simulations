"""Sustainable reward calculation"""
import pandas as pd
from .utils import RNG

PRACTICES = ['Solar','Cover-cropping','Mulching','Drip','Bio-inputs','Organic-inputs','None']

# baseline emissions tonnes CO2e/ha/cycle (dummy numbers)
E_BASE = {'Potato': 3.0, 'Onion': 2.5, 'Tomato': 4.0}

# practice effect multipliers (lower -> better reduction)
PRACTICE_EFFECT = {
    'Solar': 0.85,
    'Cover-cropping':0.7,
    'Mulching':0.8,
    'Drip':0.75,
    'Bio-inputs':0.8,
    'Organic-inputs':0.7,
    'None':1.0
}


def compute_reward(farmers_df):
    rows = []
    for _, r in farmers_df.iterrows():
        practice = RNG.choices(PRACTICES, weights=[0.08,0.12,0.10,0.15,0.10,0.10,0.35])[0]
        A = r['area_ha']
        crop = r['crop']
        Ebaseline = E_BASE[crop]
        Eactual = Ebaseline * PRACTICE_EFFECT[practice]
        # V confidence
        V = RNG.uniform(0.8,1.0) if RNG.random() < 0.8 else RNG.uniform(0.4,0.8)
        coins = max(0.0, (Ebaseline - Eactual) * A * V)
        rows.append({'farmer_id': r['farmer_id'], 'geohash': r['geohash'], 'area_ha': A, 'crop': crop, 'crop_cycle':'Rabi', 'practice': practice, 'coins': round(coins,4)})
    return pd.DataFrame(rows)


