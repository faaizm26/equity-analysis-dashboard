# equity-analysis-dashboard
Python-based computational stock dashboard.

### DISCLAIMER: 
This program is for educational purposes only and not at all to be used for financial advice or for real-world investments of any sort.

## Overview
This dashboard not only allows users to view the key financials and stock price movements of any S&P company, but it also constructs a peer group of S&P 500 companies with similar market performance to complete a relative valuation. As part of this valuation, the program returns trading premiums/discounts based on certain metrics. Furthermore, the program calculates various quantitative metrics that analyze the stock's risk and volatility relative to the market. 

The program exports all tables and metrics to Excel, through which users can download the data.

### NOTE:
This dashboard is currently limited to companies in the S&P 500 only. Please note that even within the S&P 500, if a company has not published certain key financials, the program might return errors. 

## Features
- Stock ticker input (users can choose to view data for any company's stock using its Yahoo Finance ticker)
- Key financials
- Historical stock price table
- Price movement chart with 50-day and 200-day movement averages for the past year.
- Peer group comps table with key financials
- Trading premiums/discounts based on peer valuation
- Quantitative analysis metrics

## Methods

### Comparable Company Analysis:
As part of the CCA, the program first chooses similar companies by selecting for the same GICS sub-industry. Then, narrows down peers by looking for companies with market capitalizations and revenue growth rates closest to the original company. Finally, it pick 5 top contenders and forms a peer group.

### Quantitative Metrics:
The program utilizes the daily returns to compute annualized volatility and beta to analyze risk relative to the market. It also calculates maximum drawdown and relative performance (compared to S&P 500). 

## Relevant Technologies and Tools
- Python
- Streamlit
- Plotly
- Pandas
- YFinance
- OpenPyXL

## Instructions to Run the Program:

1. Clone this repository:
   
```bash
git clone https://github.com/faaizm26/equity-analysis-dashboard.git
cd equity-analysis-dashboard
```

2. Create virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

3. Install relevant Python packages:
   
```bash
pip install streamlit yfinance pandas plotly openpyxl
```

4. Run the Streamlit app:
   
```bash
streamlit run app.py
```

## Possible Improvements
Some changes that would make this program more advanced and applicable to real-world markets include:
- An expansion beyond the S&P 500 market
- A way to retrieve stock information by using regular tickers rather than Yahoo Finance tickers
- A more complex way of forming peer valuation groups for the CCA involving a wider range of valuation multiples and analytical techniques
- Faster runtime by incorporating more efficient data retrieval and caching.
