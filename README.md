# 🌱 Smart Contracts and Green Finance in the Indian Agriculture Sector

## 📌 Overview

This repository contains a simulation framework developed as part of a research thesis exploring how **blockchain-enabled smart contracts and tokenized incentives** can transform green finance adoption in Indian agriculture.

The system integrates:

* **Periodic call auctions** for transparent price discovery
* **MSP-anchored pricing mechanisms**
* **MRV-based emission verification**
* **Tokenized sustainability rewards**

The goal is to create a **self-sustaining financial loop** where environmentally responsible farming directly improves farmers' economic outcomes.

---

## ❓ Research Question

How can smart contracts, tokenized incentives, and transparent auction mechanisms be combined to:

* Improve farmer income stability
* Incentivize sustainable agricultural practices
* Enable participation in climate finance and carbon markets

---

## 🧠 Methodology

We design a **modular simulation architecture** consisting of:

### 1. Market Simulation

* Synthetic generation of farmers and buyers
* Crop-variety-grade segmentation
* Stochastic bidding and asking behavior

(Implemented in data_generator.py)

---

### 2. Periodic Call Auction Mechanism

* Sealed-bid auction clearing at discrete time windows
* Uniform pricing via midpoint discovery
* MSP-anchored reference price
* Volatility-based price bands
* Daily price movement caps

(Implemented in auction.py)

---

### 3. Market Parameters

* MSP benchmarks
* Historical and recent price medians
* Volatility estimates
* Grade-based pricing hierarchy

(Implemented in market_params.py)

---

### 4. MRV-Based Reward Token System

* Emission baseline vs actual estimation
* Practice-based reduction multipliers
* Verification confidence weighting
* Token generation proportional to sustainability impact

(Implemented in rewards.py)

---

### 5. Simulation Pipeline

* Multi-window auction execution
* Order matching and ledger creation
* Reward token computation
* Output generation (CSV files)

(Implemented in main.py)

---

## 📊 Dataset Description

This project uses **synthetically generated data**, including:

* Farmer population (landholding categories, crop choices, yields)
* Buyer demand (quantity, bids, crop preferences)
* Market parameters (MSP, price distributions)

No external datasets are required.

---

## ⚙️ Instructions to Run the Code

### 1. Clone the repository

```bash
git clone https://github.com/aitijhya04/Green_Finance_Simulations
cd Green_Finance_Simulations
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Dependencies listed in requirements.txt include:

* pandas
* numpy
* python-dateutil

---

### 3. Run the simulation

```bash
python -m src.main
```

---

### 4. Output Files Generated

* `trade_ledger.csv` → Auction transactions
* `rewards.csv` → Sustainability tokens
* `farmers.csv` → Farmer dataset

---

## 📈 Results Summary

The simulation produces:

* **Efficient price discovery** under MSP constraints
* **Transparent matching between buyers and farmers**
* **Token rewards linked to real environmental impact**
* **Improved economic incentives for sustainable practices**

Key outputs:

* Total trades executed
* Quantity traded
* Reward tokens generated per farmer

---

## 📁 Repository Structure

```
project-name/
│
├── README.md
├── requirements.txt
│
├── data/
│   ├── raw/
│   ├── processed/
│
├── src/
│   ├── data_generator.py
│   ├── auction.py
│   ├── rewards.py
│   ├── market_params.py
│   ├── utils.py
│   ├── main.py
│
├── notebooks/
│   ├── exploratory_analysis.ipynb
│
├── results/
│   ├── figures/
│   ├── tables/
│
└── paper/
    └── final_report.pdf
```

---

## 🔧 Dependencies

* Python 3.8+
* pandas
* numpy
* python-dateutil

(Full list in `requirements.txt`)

---

## 🧩 Key Features

* Modular and extensible architecture
* Reproducible simulation pipeline
* MSP-aware auction design
* Climate-linked financial incentives
* Policy experimentation capability

---

## 🔁 Reproducibility

This repository ensures full reproducibility via:

* Deterministic random seed (`RNG = random.Random(12345)`)
* Complete simulation pipeline in `main.py`
* No external data dependencies
* Explicit parameter configuration

To reproduce results:

1. Install dependencies
2. Run simulation
3. Verify generated CSV outputs

---

## 👥 Authors

* **Aitijhya Mondal**

---

## 🎓 Faculty Supervisor

* **Prof.Aditya Sharma** *

---

## 📜 License

This project is licensed under the terms specified in the `LICENSE` file.

---

## 🚀 Future Work

* Integration with real-world mandi datasets
* Smart contract deployment (e.g., Ethereum / Hyperledger)
* Dynamic pricing models using RL/ML
* Integration with actual carbon credit registries

---
