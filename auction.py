"""Auction engine implementing the sealed-bid periodic clearing"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .market_params import get_hist_median, get_recent_median, get_msp, get_volatility, W1, W2, W3, K_BAND, DAILY_CAP_PCT
from .utils import RNG

class OrderBook:
    def __init__(self):
        # orders are dicts stored in lists
        self.buyers = []
        self.sellers = []

    def add_buyer(self, order):
        self.buyers.append(order)

    def add_seller(self, order):
        self.sellers.append(order)

    def carry_over(self):
        # keep buyers and sellers as-is; they include timestamp
        pass


class AuctionEngine:
    def __init__(self, ledger_df, last_clearing_prices=None):
        self.ledger = ledger_df
        # last clearing price per (crop, variety, grade)
        self.last_price = last_clearing_prices if last_clearing_prices is not None else {}

    def compute_reference(self, crop, grade):
        msp = get_msp(crop)
        hist = get_hist_median(crop, grade)
        recent = get_recent_median(crop, grade)
        R = W1*msp + W2*hist + W3*recent
        return R, msp, hist, recent

    def compute_band(self, crop, grade, R):
        sigma = get_volatility(crop)
        LB = max(get_msp(crop), R - K_BAND*sigma)
        UB = R + K_BAND*sigma
        return LB, UB

    def daily_cap(self, key):
        last = self.last_price.get(key, None)
        if last is None:
            return None
        low = last*(1-DAILY_CAP_PCT)
        high = last*(1+DAILY_CAP_PCT)
        return low, high

    def match_price(self, orderbook, crop, variety, grade, window_ts):
        # Filter active buyers/sellers for this crop-variety-grade
        buyers = [b for b in orderbook.buyers if b['crop']==crop and b['variety']==variety and b['grade']==grade and b['bid']>=get_msp(crop)]
        sellers = [s for s in orderbook.sellers if s['crop']==crop and s['variety']==variety and s['grade']==grade]
        if len(buyers)==0 or len(sellers)==0:
            return [], [], []

        # sort
        buyers_sorted = sorted(buyers, key=lambda x: (-x['bid'], x['timestamp']))
        sellers_sorted = sorted(sellers, key=lambda x: (x['ask'], x['timestamp']))

        # find t_max by index pair
        cum_d = 0.0
        cum_s = 0.0
        t_max = -1
        for i,(b,s) in enumerate(zip(buyers_sorted, sellers_sorted)):
            cum_d += b['quantity_q']
            cum_s += s['quantity_q']
            if b['bid'] >= s['ask']:
                t_max = i
            else:
                break
        if t_max==-1:
            return [], buyers_sorted, sellers_sorted
        # compute cumulative up to t_max
        D_t = sum(buyers_sorted[i]['quantity_q'] for i in range(t_max+1))
        S_t = sum(sellers_sorted[i]['quantity_q'] for i in range(t_max+1))
        Q = min(D_t, S_t)

        bid_t = buyers_sorted[t_max]['bid']
        ask_t = sellers_sorted[t_max]['ask']
        p_star = (bid_t + ask_t)/2.0

        # compute reference and band
        R, msp, hist, recent = self.compute_reference(crop, grade)
        LB, UB = self.compute_band(crop, grade, R)

        # clamp p_star to band
        if p_star < LB:
            p_star = LB
        if p_star > UB:
            p_star = UB

        # daily cap
        key = (crop, variety, grade)
        cap = self.daily_cap(key)
        if cap is not None:
            low, high = cap
            if p_star < low:
                p_star = low
            if p_star > high:
                p_star = high

        # now at price p_star, recompute eligible buyers and sellers
        buyers_eligible = [b for b in buyers_sorted if b['bid'] >= p_star]
        sellers_eligible = [s for s in sellers_sorted if s['ask'] <= p_star]
        if len(buyers_eligible)==0 or len(sellers_eligible)==0:
            return [], buyers_sorted, sellers_sorted
        # traded quantity
        total_d = sum(b['quantity_q'] for b in buyers_eligible)
        total_s = sum(s['quantity_q'] for s in sellers_eligible)
        Q_final = min(total_d, total_s)

        # allocate to sellers first (price asc) then buyers
        trades = []
        remaining = Q_final
        seller_idx = 0
        # random tie break for equal asks/bids
        # allocate sellers
        while remaining>1e-9 and seller_idx < len(sellers_eligible):
            s = sellers_eligible[seller_idx]
            take = min(s['quantity_q'], remaining)
            trades.append({'seller':s, 'buyer':None, 'qty':take, 'price':p_star})
            s['quantity_q'] -= take
            remaining -= take
            seller_idx += 1
        # now match to buyers by priority
        remaining = Q_final
        buyer_idx = 0
        buyer_allocs = []
        while remaining>1e-9 and buyer_idx < len(buyers_eligible):
            b = buyers_eligible[buyer_idx]
            take = min(b['quantity_q'], remaining)
            buyer_allocs.append({'buyer':b, 'qty':take, 'price':p_star})
            b['quantity_q'] -= take
            remaining -= take
            buyer_idx += 1

        # produce ledger entries pairing sequentially (FIFO style)
        # pair by walking seller list and buyer_allocs
        s_ptr = 0
        b_ptr = 0
        s_rem = sellers_eligible[0]['quantity_q'] if sellers_eligible else 0
        # Instead, reconstruct from stored remaining amounts above: use original copies
        sellers_copy = [dict(s) for s in sellers_eligible]
        buyers_copy = [dict(b) for b in buyers_eligible]
        # Recompute original quantities before allocation
        # For simplicity, we will pair using a simple loop consuming from sellers and buyers
        sid = 0
        bid_i = 0
        s_remaining = sum(s['quantity_q'] for s in sellers_eligible) + 0.0
        # but we modified quantities earlier; rebuild originals via fresh sort from orderbook
        sellers_orig = [s for s in sellers_sorted if s['ask']<=p_star]
        buyers_orig = [b for b in buyers_sorted if b['bid']>=p_star]

        s_ptr = 0
        b_ptr = 0
        s_left = sellers_orig[s_ptr]['quantity_q']
        b_left = buyers_orig[b_ptr]['quantity_q']
        qty_to_trade = Q_final
        while qty_to_trade>1e-9 and s_ptr < len(sellers_orig) and b_ptr < len(buyers_orig):
            take = min(s_left, b_left, qty_to_trade)
            trace = {
                'order_id': str(RNG.getrandbits(64)),
                'date': window_ts.isoformat(),
                'crop': crop,
                'variety': variety,
                'grade': grade,
                'qty_q': round(take,3),
                'final_price_per_q': round(p_star,2),
                'seller_id': sellers_orig[s_ptr]['farmer_id'],
                'buyer_id': buyers_orig[b_ptr]['buyer_id']
            }
            self.ledger.append(trace)
            s_left -= take
            b_left -= take
            qty_to_trade -= take
            if abs(s_left) < 1e-9:
                s_ptr += 1
                if s_ptr < len(sellers_orig):
                    s_left = sellers_orig[s_ptr]['quantity_q']
            if abs(b_left) < 1e-9:
                b_ptr += 1
                if b_ptr < len(buyers_orig):
                    b_left = buyers_orig[b_ptr]['quantity_q']

        # update last clearing
        self.last_price[(crop,variety,grade)] = p_star

        # remove fulfilled orders from original orderbook and preserve partials carry-over
        # (orders in orderbook are mutable dicts; reflect reductions)
        # For simplicity we will let main driver rebuild orderbook carry-overs based on remaining quantities in buyers_sorted and sellers_sorted after allocations

        return self.ledger, buyers_sorted, sellers_sorted

