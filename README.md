# Trading Bot

![Python Version](https://img.shields.io/badge/Python-3.12%2B-blue)
![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen)
![License](https://img.shields.io/badge/License-MIT-lightgrey)
![Platform](https://img.shields.io/badge/Platform-Alpaca%20API-orange)

An automated trading bot built on the **Alpaca API**, capable of executing trades across stocks, options, crypto, and other supported assets. This project is under active development throughout the summer and is designed to evolve into a robust quantitative trading system.

The bot currently runs **fully automated**, executing up to **five cycles every five seconds** while analyzing **15‑minute candles**. Its core strategy uses **EMA‑12** and **EMA‑26** crossovers to identify bullish or bearish trends and trigger buy/sell signals. After entering a position, the bot manages trades using **stop‑loss** and **take‑profit** logic to control risk.

Future development includes:

- Options‑trading protocols  
- Quantitative trading models  
- Improved signal generation  
- Expanded asset support  

Target performance: **10–15% ROI**, consistent with industry benchmarks for automated systems.

---

# Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Bot](#running-the-bot)
- [Project Structure](#project-structure)
- [Contact](#contact)

---

# Features
- ✔️ Fully automated trading execution  
- ✔️ EMA‑based trend detection (EMA‑12 / EMA‑26)  
- ✔️ Stop‑loss and take‑profit risk management  
- ✔️ High‑frequency scanning (every 5 seconds)  
- ✔️ Alpaca API integration  
- ✔️ Modular design for future strategies  

---

# Requirements
- Python **3.12+**  
- Alpaca **paper trading** account  
- Jupyter Notebook  
- Internet connection  

---

# Installation

## 1. Create an Alpaca Account
Sign up for a free paper‑trading account:  
https://alpaca.markets/

## 2. Install Python
Download Python 3.12 or higher:  
https://www.python.org/downloads/

## 3. Install Jupyter Notebook
Open **Command Prompt** and run:

```bash
pip install jupyter
```
## 4. Download the Repository
Clone the repository with files:
- pythontradingbot.ipynb
- accountid_example.py

---

# Configuration

## Add Your API Key
Log into your Alpaca dashboard and locate your:
- API Key
- Secret Key
- Paper Trading Account ID

Paste both values into accountid_example.txt, then rename the file:

```bash
accountid.py
```
Place both files — accountid.py and pythontradingbot.ipynb — in the same directory.

---
# Running the Bot
Launch Jupyter Notebook by opening Command Prompt and typing:

```bash
jupyter notebook
```
Once the Jupyter interface opens, select the notebook file and run all cells.
The bot will begin executing automatically.

---
# Project Structure
```bash
/TradingBot
│
├── pythontradingbot.ipynb        # Main bot logic
├── accountid.py                  # User API keys (local only)
├── README.md                     # Project documentation
└── /data                         # (Optional) Logs, exports, etc.
```

---
# Contact
For any questions or feedback, feel free to reach out to me at:
```bash
nickbeharry2003@gmail.com
```