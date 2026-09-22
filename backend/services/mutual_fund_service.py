"""
AlphaLens Mutual Fund Intelligence & Recommendation Engine
Curates and ranks top Indian direct mutual funds across categories,
evaluates risk-adjusted alpha/Sharpe metrics, and suggests optimal funds based on investor profile.
"""

from typing import Dict, Any, List, Optional


MUTUAL_FUND_CATALOG: List[Dict[str, Any]] = [
    # -------------------------------------------------------------------------
    # 1. Flexi Cap Funds (Core Wealth Compounders)
    # -------------------------------------------------------------------------
    {
        "id": "parag-parikh-flexi-cap",
        "name": "Parag Parikh Flexi Cap Fund",
        "category": "Flexi Cap",
        "amc": "PPFAS Mutual Fund",
        "plan": "Direct - Growth",
        "aum_cr": 72450,
        "cagr_1y": 28.4,
        "cagr_3y": 21.8,
        "cagr_5y": 24.5,
        "expense_ratio": 0.62,
        "alpha_vs_bench": 5.4,
        "sharpe_ratio": 1.95,
        "risk_tier": "Moderate to High",
        "min_sip": 1000,
        "fund_manager": "Rajeev Thakkar",
        "suitability": "Ideal core equity anchor fund for 5+ year horizons seeking global diversification (holds ~15% US tech like Alphabet & Microsoft).",
        "verdict": "🌟 TOP RATED (Best Overall Flexi Cap)",
        "why_recommended": [
            "Disciplined value investing philosophy with strong cash-rich allocation.",
            "Consistently beats Nifty 500 TRI with industry-leading downside risk protection.",
            "Low portfolio turnover with high skin-in-the-game from AMC promoters."
        ]
    },
    {
        "id": "jm-flexicap-fund",
        "name": "JM Flexicap Fund",
        "category": "Flexi Cap",
        "amc": "JM Financial Mutual Fund",
        "plan": "Direct - Growth",
        "aum_cr": 12850,
        "cagr_1y": 44.2,
        "cagr_3y": 29.5,
        "cagr_5y": 26.8,
        "expense_ratio": 0.48,
        "alpha_vs_bench": 9.2,
        "sharpe_ratio": 2.24,
        "risk_tier": "High",
        "min_sip": 500,
        "fund_manager": "Satish Ramanathan",
        "suitability": "Aggressive investors seeking high momentum alpha across large, mid, and small cap market segments.",
        "verdict": "🚀 TOP MOMENTUM (Highest 3Y Return in Category)",
        "why_recommended": [
            "Agile sector rotation capturing high-growth infrastructure, capital goods, and defense rallies.",
            "Exceptional Sharpe ratio (2.24) and low expense ratio (0.48%)."
        ]
    },

    # -------------------------------------------------------------------------
    # 2. Large Cap / Index Funds (Foundation & Safe Growth)
    # -------------------------------------------------------------------------
    {
        "id": "uti-nifty-50-index",
        "name": "UTI Nifty 50 Index Fund",
        "category": "Large Cap / Index",
        "amc": "UTI Mutual Fund",
        "plan": "Direct - Growth",
        "aum_cr": 21340,
        "cagr_1y": 24.6,
        "cagr_3y": 15.2,
        "cagr_5y": 17.8,
        "expense_ratio": 0.18,
        "alpha_vs_bench": 0.0,
        "sharpe_ratio": 1.48,
        "risk_tier": "Moderate",
        "min_sip": 500,
        "fund_manager": "Sharwan Kumar Goyal",
        "suitability": "Beginners, conservative equity investors, and core retirement portfolios seeking India's top 50 bluechips with lowest cost.",
        "verdict": "🛡️ BEST LOW-COST CORE (Lowest Tracking Error)",
        "why_recommended": [
            "Minimal expense ratio (0.18%) with best-in-class tracking error (< 0.03%).",
            "Eliminates fund manager bias by capturing 100% of India's economic growth."
        ]
    },
    {
        "id": "hdfc-nifty-next-50",
        "name": "HDFC Nifty Next 50 Index Fund",
        "category": "Large & Mid Cap / Index",
        "amc": "HDFC Mutual Fund",
        "plan": "Direct - Growth",
        "aum_cr": 8420,
        "cagr_1y": 48.2,
        "cagr_3y": 22.4,
        "cagr_5y": 20.8,
        "expense_ratio": 0.30,
        "alpha_vs_bench": 0.0,
        "sharpe_ratio": 1.76,
        "risk_tier": "High",
        "min_sip": 500,
        "fund_manager": "Arun Agarwal",
        "suitability": "Investors wanting exposure to future Nifty 50 bluechips (ranks 51-100) with higher growth velocity.",
        "verdict": "⚡ HIGH GROWTH PASSIVE (Nifty Next 50)",
        "why_recommended": [
            "Captures emerging large caps with multibagger momentum at low passive cost.",
            "Higher 3Y/5Y returns than core Nifty 50 with modest additional volatility."
        ]
    },

    # -------------------------------------------------------------------------
    # 3. Mid Cap Funds (High Growth Engine)
    # -------------------------------------------------------------------------
    {
        "id": "motilal-oswal-midcap",
        "name": "Motilal Oswal Midcap Fund",
        "category": "Mid Cap",
        "amc": "Motilal Oswal Mutual Fund",
        "plan": "Direct - Growth",
        "aum_cr": 18450,
        "cagr_1y": 52.8,
        "cagr_3y": 34.2,
        "cagr_5y": 28.5,
        "expense_ratio": 0.65,
        "alpha_vs_bench": 11.4,
        "sharpe_ratio": 2.45,
        "risk_tier": "Very High",
        "min_sip": 500,
        "fund_manager": "Niket Shah",
        "suitability": "Aggressive wealth-builders aiming for market-crushing returns with 5 to 7+ year horizon.",
        "verdict": "🏆 BEST MID CAP (Category Leader)",
        "why_recommended": [
            "High-conviction concentrated stock selection focusing on market leaders with high ROCE (e.g. Trent, Kalyan Jewellers).",
            "Highest 3-year CAGR (34.2%) across all midcap funds."
        ]
    },

    # -------------------------------------------------------------------------
    # 4. Small Cap Funds (Maximum Aggressive Growth)
    # -------------------------------------------------------------------------
    {
        "id": "quant-small-cap",
        "name": "Quant Small Cap Fund",
        "category": "Small Cap",
        "amc": "Quant Mutual Fund",
        "plan": "Direct - Growth",
        "aum_cr": 24900,
        "cagr_1y": 46.5,
        "cagr_3y": 32.4,
        "cagr_5y": 38.6,
        "expense_ratio": 0.77,
        "alpha_vs_bench": 14.2,
        "sharpe_ratio": 2.38,
        "risk_tier": "Very High",
        "min_sip": 1000,
        "fund_manager": "Sandeep Tandon",
        "suitability": "High-risk appetite investors with 7-10+ year horizon ready to navigate small-cap volatility cycles.",
        "verdict": "🔥 HIGHEST 5Y CAGR (38.6% p.a.)",
        "why_recommended": [
            "Proprietary VLRT (Valuation, Liquidity, Risk, Timing) quant framework with high-frequency dynamic rebalancing.",
            "Exceptional 5-year track record multiplying capital 5x+ over 5 years."
        ]
    },
    {
        "id": "nippon-india-small-cap",
        "name": "Nippon India Small Cap Fund",
        "category": "Small Cap",
        "amc": "Nippon India Mutual Fund",
        "plan": "Direct - Growth",
        "aum_cr": 58900,
        "cagr_1y": 38.8,
        "cagr_3y": 28.6,
        "cagr_5y": 31.4,
        "expense_ratio": 0.68,
        "alpha_vs_bench": 8.5,
        "sharpe_ratio": 2.10,
        "risk_tier": "Very High",
        "min_sip": 500,
        "fund_manager": "Samir Rachh",
        "suitability": "Investors wanting well-diversified, institutional-grade small cap compounding (200+ holdings).",
        "verdict": "💎 BEST DIVERSIFIED SMALL CAP",
        "why_recommended": [
            "Highly diversified portfolio minimizing single-stock blowup risk in volatile small caps.",
            "Longest consistent performance track record across 10+ market cycles."
        ]
    },

    # -------------------------------------------------------------------------
    # 5. ELSS Tax Saver Funds (Section 80C Tax Saving)
    # -------------------------------------------------------------------------
    {
        "id": "mirae-asset-elss-tax-saver",
        "name": "Mirae Asset ELSS Tax Saver Fund",
        "category": "ELSS Tax Saver",
        "amc": "Mirae Asset Mutual Fund",
        "plan": "Direct - Growth",
        "aum_cr": 23400,
        "cagr_1y": 31.2,
        "cagr_3y": 18.6,
        "cagr_5y": 21.4,
        "expense_ratio": 0.58,
        "alpha_vs_bench": 3.8,
        "sharpe_ratio": 1.72,
        "risk_tier": "High",
        "min_sip": 500,
        "fund_manager": "Neelesh Surana",
        "suitability": "Taxpayers wanting Section 80C deductions (up to ₹1.5L) with the shortest lock-in period (3 years) vs PPF (15 years) or FD (5 years).",
        "verdict": "🧾 BEST ELSS TAX SAVER",
        "why_recommended": [
            "Consistent top-quartile performance managed by legendary stock-picker Neelesh Surana.",
            "Shortest tax-saving lock-in period (3 years) with superior equity compounding."
        ]
    },

    # -------------------------------------------------------------------------
    # 6. Hybrid & Balanced Advantage Funds (Safe & Defensive)
    # -------------------------------------------------------------------------
    {
        "id": "icici-pru-balanced-advantage",
        "name": "ICICI Prudential Balanced Advantage Fund",
        "category": "Dynamic Asset Allocation / BAF",
        "amc": "ICICI Prudential Mutual Fund",
        "plan": "Direct - Growth",
        "aum_cr": 61200,
        "cagr_1y": 18.2,
        "cagr_3y": 14.8,
        "cagr_5y": 15.6,
        "expense_ratio": 0.72,
        "alpha_vs_bench": 2.5,
        "sharpe_ratio": 1.65,
        "risk_tier": "Low to Moderate",
        "min_sip": 500,
        "fund_manager": "Sankaran Naren",
        "suitability": "Conservative investors, senior citizens, or tactical money seeking automatic equity-debt rebalancing without crash fear.",
        "verdict": "🛡️ BEST DEFENSIVE HYBRID",
        "why_recommended": [
            "Proprietary in-house P/B model automatically cuts equity when markets are expensive and buys aggressively when markets crash.",
            "Downside protection is superior with equity taxation benefits."
        ]
    }
]


class MutualFundService:
    def get_all_funds(self) -> List[Dict[str, Any]]:
        return MUTUAL_FUND_CATALOG

    def get_funds_by_category(self, category: str) -> List[Dict[str, Any]]:
        cat_lower = category.lower()
        return [f for f in MUTUAL_FUND_CATALOG if cat_lower in f["category"].lower()]

    def get_fund_by_name(self, query: str) -> Optional[Dict[str, Any]]:
        q = query.lower().strip()
        for f in MUTUAL_FUND_CATALOG:
            if q in f["id"] or q in f["name"].lower():
                return f
        return None

    def recommend_portfolio(self, risk_profile: str = "moderate", horizon_years: int = 5) -> Dict[str, Any]:
        """Provides custom personalized mutual fund allocation based on risk and horizon."""
        risk = risk_profile.lower()

        if "conservative" in risk or horizon_years < 3:
            allocation = [
                {"fund": "UTI Nifty 50 Index Fund", "category": "Large Cap Index", "weight_pct": 50, "rationale": "Rock-solid bluechip foundation with minimal volatility."},
                {"fund": "ICICI Prudential Balanced Advantage Fund", "category": "Hybrid / BAF", "weight_pct": 50, "rationale": "Dynamic debt-equity asset allocation cushioning market drops."}
            ]
            expected_cagr = "12% - 14% p.a."
            strategy_name = "Conservative Capital Compounder"
        elif "aggressive" in risk or horizon_years >= 7:
            allocation = [
                {"fund": "Parag Parikh Flexi Cap Fund", "category": "Flexi Cap", "weight_pct": 35, "rationale": "Global + domestic core compounder with downside protection."},
                {"fund": "Motilal Oswal Midcap Fund", "category": "Mid Cap", "weight_pct": 35, "rationale": "High-conviction high ROCE midcap winners."},
                {"fund": "Quant Small Cap Fund", "category": "Small Cap", "weight_pct": 20, "rationale": "High-alpha quant-driven small cap alpha engine."},
                {"fund": "UTI Nifty 50 Index Fund", "category": "Large Cap Index", "weight_pct": 10, "rationale": "Core liquidity anchor."}
            ]
            expected_cagr = "18% - 22% p.a."
            strategy_name = "Aggressive Multi-Cap Alpha Accelerator"
        else:  # Moderate (Standard 3-5 Years)
            allocation = [
                {"fund": "Parag Parikh Flexi Cap Fund", "category": "Flexi Cap", "weight_pct": 40, "rationale": "All-weather multi-cap core with international diversification."},
                {"fund": "UTI Nifty 50 Index Fund", "category": "Large Cap Index", "weight_pct": 30, "rationale": "Low cost exposure to top 50 Indian enterprises."},
                {"fund": "Motilal Oswal Midcap Fund", "category": "Mid Cap", "weight_pct": 20, "rationale": "Midcap growth kicker for outperformance."},
                {"fund": "Nippon India Small Cap Fund", "category": "Small Cap", "weight_pct": 10, "rationale": "Well-diversified small cap booster."}
            ]
            expected_cagr = "15% - 17% p.a."
            strategy_name = "Balanced Multi-Asset Wealth Builder"

        return {
            "strategy_name": strategy_name,
            "risk_profile": risk.capitalize(),
            "horizon_years": horizon_years,
            "expected_cagr_range": expected_cagr,
            "recommended_allocation": allocation,
            "pro_tips": [
                "Always choose 'Direct - Growth' plans over 'Regular' plans to save 0.5% - 1.0% in commissions annually.",
                "Automate monthly SIP on your salary date (e.g. 5th of every month) for rupee-cost averaging.",
                "Enable 10% Annual Step-up SIP to double your final 15-year corpus."
            ]
        }


mutual_fund_service = MutualFundService()
