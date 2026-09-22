# AlphaLens Data Provenance & Lineage Specification

## 1. Overview
This document records the exact provenance, schema specifications, feature definitions, and transformation methodology for all market, fundamental, sentiment, and macro datasets used across the **AlphaLens (FinSight)** system.

---

## 2. Universe Coverage
- **Primary Market**: National Stock Exchange of India (NSE) Large-Cap & Mid-Cap universe
- **Benchmark Indices**: NIFTY 50 (`^NSEI`), NIFTY BANK (`^NSEBANK`), S&P BSE SENSEX (`^BSESN`), INDIA VIX
- **Equity Universe (Active Tracked)**:
  1. `RELIANCE` — Reliance Industries Ltd (Energy / Conglomerate)
  2. `TCS` — Tata Consultancy Services Ltd (Information Technology)
  3. `HDFCBANK` — HDFC Bank Ltd (Banking & Financial Services)
  4. `INFY` — Infosys Ltd (Information Technology)
  5. `ICICIBANK` — ICICI Bank Ltd (Banking & Financial Services)
  6. `TATAMOTORS` — Tata Motors Ltd (Automobile)
  7. `BHARTIARTL` — Bharti Airtel Ltd (Telecommunications)
  8. `ITC` — ITC Ltd (FMCG / Diversified)
  9. `LT` — Larsen & Toubro Ltd (Infrastructure & Engineering)
  10. `SBIN` — State Bank of India (Public Sector Banking)
  11. `KOTAKBANK` — Kotak Mahindra Bank Ltd (Banking)
  12. `HINDUNILVR` — Hindustan Unilever Ltd (FMCG)
  13. `BAJFINANCE` — Bajaj Finance Ltd (Non-Banking Financials)
  14. `MARUTI` — Maruti Suzuki India Ltd (Automobile)
  15. `SUNPHARMA` — Sun Pharmaceutical Industries Ltd (Healthcare / Pharma)
- **Temporal Coverage**: 5 Years (1,250+ Trading Days per asset, comprising ~18,750 asset-day observation vectors)
- **Frequency**: Daily OHLCV + Intraday tick simulation for live updates

---

## 3. Dataset Schemas & Provenance

### A. Market OHLCV & Technical Features (`prices/` & `stock_features.parquet`)
- **Fields**:
  - `date`: ISO-8601 Trading date (`YYYY-MM-DD`)
  - `ticker`: Standard NSE symbol
  - `open`, `high`, `low`, `close`: Adjusted market prices (INR)
  - `volume`: Daily share volume
  - `return_1d`, `return_3d`, `return_5d`, `return_20d`: Continuous log/percentage price changes
  - `sma_20`, `sma_50`, `sma_200`: Simple Moving Averages
  - `ema_20`: Exponential Moving Average
  - `rsi_14`: Relative Strength Index (14-period Wilder's smoothing)
  - `macd`, `macd_signal`, `macd_hist`: Moving Average Convergence Divergence (12, 26, 9)
  - `bollinger_upper`, `bollinger_lower`, `bollinger_pct`: Bollinger Bands (20-period, 2-std)
  - `atr_14`: Average True Range (14-period)
  - `obv`: On-Balance Volume
  - `volatility_20d`, `volatility_60d`: Annualized rolling standard deviation of daily returns
  - `beta`: 60-day rolling covariance vs NIFTY 50 / variance of NIFTY 50

### B. Financial News & FinBERT Sentiment Features (`news/` & `news_features.parquet`)
- **Fields**:
  - `headline`: Curated financial headline
  - `timestamp`: Publication timestamp
  - `ticker`: Target company
  - `finbert_sentiment`: Continuous polarity score in range `[-1.0, +1.0]` (Negative to Positive)
  - `news_impact`: Categorical weighting (`LOW`, `MEDIUM`, `HIGH`)
  - `company_relevance`: Target entity relevance score `[0.0, 1.0]`
  - `sentiment_momentum_5d`: 5-day exponential decay weighted sentiment average

### C. Corporate Fundamentals (`fundamentals/`)
- **Fields**:
  - `pe_ratio`: Trailing twelve-month Price-to-Earnings
  - `pb_ratio`: Price-to-Book ratio
  - `roe`: Return on Equity (%)
  - `roce`: Return on Capital Employed (%)
  - `debt_equity`: Total Debt to Shareholder Equity ratio
  - `revenue_growth_yoy`: YoY Quarterly Revenue Growth rate (%)
  - `eps_growth_yoy`: YoY Quarterly Earnings Per Share Growth rate (%)

### D. Market Regime & Macro Series (`macro/`)
- **Fields**:
  - `nifty_return_1d`, `nifty_return_5d`: Benchmark market returns
  - `sector_return_1d`: Sector relative performance
  - `india_vix`: Market implied volatility index
  - `market_regime`: Classified regime (`BULL_TREND`, `BEAR_TREND`, `HIGH_VOLATILITY`, `RANGEBOUND`)

---

## 4. Target Variables & Leakage Prevention
- `target_direction_1d`: Binary label (`1` if `close[t+1] > close[t]`, else `0`)
- `target_direction_3d`: Binary label (`1` if `close[t+3] > close[t]`, else `0`)
- `target_direction_5d`: Binary label (`1` if `close[t+5] > close[t]`, else `0`)
- `target_return_1d`: Actual percentage return at `t+1`
- `target_return_5d`: Actual percentage return at `t+5`

> **Leakage Rules**:
> 1. All rolling indicators (SMA, RSI, MACD, Volatility) are computed strictly on information available up to market close of date `t`.
> 2. Walk-forward testing is strictly out-of-sample: folds are partitioned chronologically with an expansion window. Training weights are never fitted on future test slices.
