import plotly.graph_objects as go
import yfinance as yf
import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
from math import sqrt

st.set_page_config(layout="wide")
st.title("Equity Analysis Dashboard")
ticker_input = st.text_input(
    "Enter the company's Yahoo Finance ticker:", "NVDA")

company = yf.Ticker(ticker_input)
data = company.history(period="1y")


@st.cache_data
def metrics(symbol):
    name = yf.Ticker(symbol)
    market_cap = name.info.get("marketCap")
    forward_PE = name.info.get("forwardPE")
    trailing_PE = name.info.get("trailingPE")
    total_revenue = name.info.get("totalRevenue")
    ev_to_ebitda = name.info.get("enterpriseToEbitda")
    rev_growth = name.info.get("revenueGrowth")
    return market_cap, forward_PE, trailing_PE, total_revenue, ev_to_ebitda, rev_growth


market_cap, forward_PE, trailing_PE, total_revenue, ev_to_ebitda, rev_growth = metrics(
    ticker_input)


def cap_size(market_cap):
    if market_cap == None:
        return None
    elif 0 <= market_cap <= 2e9:
        company_size = "Small-cap"
    elif 2e9 < market_cap <= 10e9:
        company_size = "Mid-cap"
    else:
        company_size = "Large-cap"

    return company_size


company_size = cap_size(market_cap)
print(company_size)

st.subheader("Key Financials")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Market Cap", f"${market_cap/1e12:.2f}T")
with col2:
    st.metric("Total Revenue", f"{total_revenue/1e9:.2f}B")
with col3:
    st.metric("Trailing P/E", f"{trailing_PE:.1f}x")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Forward P/E", f"{forward_PE:.1f}x")
with col2:
    st.metric("EV/EBITDA", f"{ev_to_ebitda:.1f}x")
with col3:
    st.metric("Quarterly YoY Revenue Growth", f"{rev_growth:.1%}")

if data.empty:
    st.error("The ticker was not recognized. Please enter a valid ticker.")
else:
    st.dataframe(data)
    moving_50 = data["Close"].rolling(window=50).mean()
    moving_200 = data["Close"].rolling(window=200).mean()

    fig = go.Figure(data=[go.Candlestick(x=data.index, open=data["Open"],
                                         high=data["High"], low=data["Low"], close=data["Close"], name="Price")])

    fig.add_trace(go.Scatter(x=data.index, y=moving_50, name="50-Day MA"))
    fig.add_trace(go.Scatter(x=data.index, y=moving_200, name="200-Day MA"))

    fig.update_layout(title=f"{ticker_input} Historical Price",
                      xaxis_title="Date", yaxis_title="Price (USD)")
    st.plotly_chart(fig)

sp_500 = pd.read_csv(
    "constituents.csv")

sub_industry = sp_500.loc[sp_500["Symbol"]
                          == ticker_input, "GICS Sub-Industry"].iloc[0]
comparable_comps = sp_500[sp_500["GICS Sub-Industry"] == sub_industry]

final_comps = []
final_metrics = []
growth_diffs = []
for symbol in comparable_comps["Symbol"]:
    comparable_company = yf.Ticker(symbol)
    comp_market_cap, comp_forward_PE, comp_trailing_PE, comp_total_revenue, comp_ev_to_ebitda, comp_rev_growth = metrics(
        symbol)
    comps_metrics = [comp_market_cap, comp_forward_PE, comp_trailing_PE,
                     comp_total_revenue, comp_ev_to_ebitda, comp_rev_growth]
    comps_size = cap_size(comp_market_cap)
    if symbol != ticker_input and (company_size == comps_size or (market_cap*0.5) <= comp_market_cap <= (market_cap*3)):
        growth_diff = abs(rev_growth - comp_rev_growth)
        growth_diffs.append(growth_diff)
        final_comps.append(symbol)
        final_metrics.append(comps_metrics)
closest_comps = (sorted(zip(final_comps, growth_diffs, final_metrics)))[:5]

peer_group = [comp[0] for comp in closest_comps]
peer_group_growth = [comp[1] for comp in closest_comps]
peer_group_metrics = [comp[2] for comp in closest_comps]


comps_table = pd.DataFrame(peer_group_metrics, columns=[
                           "Market Cap", "Forward PE", "Trailing PE", "Total Revenue", "EV/EBITDA", "Quarterly YoY Revenue Growth"])
comps_table.insert(0, "Company", peer_group)
comps_table.index = comps_table.index + 1

st.subheader("Comparable Company Analysis")
st.caption(
    "S&P 500 peers chosen based on sub-industry, market capitalization, and enterprise mutiple")
st.dataframe(comps_table)
peer_valuation = comps_table[["Forward PE", "Trailing PE", "EV/EBITDA"]]
peer_median = peer_valuation.median()

forward_PE_val = (forward_PE/peer_median["Forward PE"]) - 1
trailing_PE_val = (trailing_PE/peer_median["Trailing PE"]) - 1
ev_to_ebitda_val = (ev_to_ebitda/peer_median["EV/EBITDA"]) - 1

st.subheader("Peer Group Valuation")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Forward PE Premium/Discount", f"{forward_PE_val:+.1%}")
with col2:
    st.metric("Trailing PE Premium/Discount", f"{trailing_PE_val:+.1%}")
with col3:
    st.metric("EV/EBITDA Premium/Discount", f"{ev_to_ebitda_val:+.1%}")

returns = (data["Close"].pct_change()).dropna()
annual_vol = returns.std()*sqrt(252)

market = yf.Ticker("^GSPC")
market_data = market.history(period="1y")
market_return = (market_data["Close"].pct_change()).dropna()

beta = returns.cov(market_return)/market_return.var()
max_drawdown = ((data["Close"] - data["Close"].cummax()) /
                data["Close"].cummax()).min()


total_return = (data["Close"].dropna()).iloc[-1] / \
    (data["Close"].dropna()).iloc[0]
total_market_return = (market_data["Close"].dropna()).iloc[-1] / \
    (market_data["Close"].dropna()).iloc[0]

rel_perform = total_return - total_market_return

st.subheader("Quantitative Analysis Metrics")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Annualized Volatility", f"{annual_vol:.1%}")
with col2:
    st.metric("Beta", f"{beta:.2f}")
with col3:
    st.metric("Maximum Drawdown", f"{max_drawdown:+.1%}")
with col4:
    st.metric("Relative Performance", f"{rel_perform:+.1%}")

key_financials = pd.DataFrame({"Key Financials": ["Market Cap", "Total Revenue", "Forward PE", "Trailing PE", "EV/EBITDA",
                              "Quarterly YoY Revenue Growth"], "Value": [market_cap, total_revenue, forward_PE, trailing_PE, ev_to_ebitda, rev_growth]})
quant_analysis = pd.DataFrame({"Quantitative Analysis Metrics": [
                              "Annualized Volatility", "Beta", "Maximum Drawdown", "Relative Perfrormance"], "Value": [annual_vol, beta, max_drawdown, rel_perform]})
buffer_bytes = BytesIO()

with pd.ExcelWriter(buffer_bytes, engine="openpyxl") as writer:
    comps_table.to_excel(
        writer, sheet_name=f"{ticker_input} Comparable Company Analysis", index=False)
    key_financials.to_excel(
        writer, sheet_name=f"{ticker_input} Key Financials", index=False)
    quant_analysis.to_excel(
        writer, sheet_name=f"{ticker_input} Quantitative Analysis", index=False)

excel_export = buffer_bytes.getvalue()

st.download_button(label=f"Download {ticker_input} Equity Analysis as an Excel file",
                   data=excel_export, file_name=f"{ticker_input}_Analysis.xlsx")
