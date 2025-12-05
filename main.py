"""Main simulation driver"""
import pandas as pd
from datetime import datetime, timedelta, time
from .data_generator import generate_farmers, generate_buyers
from .auction import OrderBook, AuctionEngine
from .rewards import compute_reward
from .market_params import MSP
from .utils import RNG


def run_simulation():
    # generate population
    farmers = generate_farmers(100)
    buyers = generate_buyers(150)

    # create initial sellers list from farmers (each farmer submits single lot of their produce)
    sellers = []
    for _, f in farmers.iterrows():
        sellers.append({'farmer_id': f['farmer_id'], 'crop': f['crop'], 'variety': f['variety'], 'grade': RNG.choice(['Super','A','B','C']), 'quantity_q': f['quantity_q'], 'ask': round(RNG.gauss(MSP[f['crop']]*1.0, MSP[f['crop']]*0.12)), 'timestamp': datetime.combine(datetime.today(), time(6,0))})

    # split the day into 20 windows from 6:00 to 16:00
    start = datetime.combine(datetime.today(), time(6,0))
    windows = [start + timedelta(minutes=30*i) for i in range(20)]

    # ledger as list (will be appended with dicts)
    ledger = []
    orderbook = OrderBook()
    # seed orderbook with initial sellers (they submit to nearest window based on timestamp)
    # Randomly assign sellers to windows
    for s in sellers:
        s['timestamp'] = RNG.choice(windows)
        orderbook.add_seller(dict(s))
    # assign buyers to windows too
    for _, b in buyers.iterrows():
        ord = {'buyer_id': b['buyer_id'], 'crop': b['crop'], 'variety': b['variety'], 'grade': b['grade'], 'quantity_q': b['quantity_q'], 'bid': b['bid'], 'timestamp': RNG.choice(windows)}
        orderbook.add_buyer(ord)

    engine = AuctionEngine(ledger_df=ledger, last_clearing_prices={})

    # simulation: iterate windows sequentially
    for w in windows:
        # pick a crop-variety-grade to clear this window probabilistically from those present
        # gather unique tuples present in orderbook at or before w
        buyers_avail = [b for b in orderbook.buyers if b['timestamp']<=w and b['quantity_q']>0]
        sellers_avail = [s for s in orderbook.sellers if s['timestamp']<=w and s['quantity_q']>0]
        if not buyers_avail or not sellers_avail:
            continue
        tuples = list(set((b['crop'], b['variety'], b['grade']) for b in buyers_avail))
        if len(tuples)==0:
            continue
        crop,variety,grade = RNG.choice(tuples)
        # create a temporary book for this window (only include orders with timestamp <= w)
        tmp_book = OrderBook()
        for b in [x.copy() for x in orderbook.buyers if x['timestamp']<=w and x['quantity_q']>0]:
            tmp_book.add_buyer(b)
        for s in [x.copy() for x in orderbook.sellers if x['timestamp']<=w and x['quantity_q']>0]:
            tmp_book.add_seller(s)

        ledger_result, buyers_sorted, sellers_sorted = engine.match_price(tmp_book, crop, variety, grade, w)

        # reflect carry over reductions back to main orderbook
        # For buyers: match by buyer_id and reduce quantities according to buyers_sorted current quantities (buyers_sorted were mutated)
        buyer_map = {b['buyer_id']:b['quantity_q'] for b in buyers_sorted}
        for ob in orderbook.buyers:
            if ob['buyer_id'] in buyer_map:
                ob['quantity_q'] = buyer_map[ob['buyer_id']]
        seller_map = {s['farmer_id']:s['quantity_q'] for s in sellers_sorted}
        for os in orderbook.sellers:
            if os['farmer_id'] in seller_map:
                os['quantity_q'] = seller_map[os['farmer_id']]

    # build pandas ledger
    ledger_df = pd.DataFrame(ledger)
    # rewards
    rewards_df = compute_reward(farmers)

    # summary
    total_buyers = len(set(ledger_df['buyer_id'])) if not ledger_df.empty else 0
    total_sellers = len(set(ledger_df['seller_id'])) if not ledger_df.empty else 0
    total_traded_q = ledger_df['qty_q'].sum() if not ledger_df.empty else 0

    print('Simulation complete')
    print('Total trades:', len(ledger_df))
    print('Unique buyers fulfilled:', total_buyers)
    print('Unique sellers fulfilled:', total_sellers)
    print('Total quantity traded (quintal):', total_traded_q)

    # save outputs
    ledger_df.to_csv('trade_ledger.csv', index=False)
    rewards_df.to_csv('rewards.csv', index=False)
    farmers.to_csv('farmers.csv', index=False)
    print('Saved ledger.csv, rewards.csv, farmers.csv')

if __name__=='__main__':
    run_simulation()