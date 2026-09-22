"""
AlphaLens IPO Intelligence & Recommendation Engine
Tracks active, upcoming, and recent Indian IPOs with live Grey Market Premium (GMP),
financial health scorecards, valuation multiples, and explicit APPLY vs AVOID verdicts.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


IPO_CATALOG: List[Dict[str, Any]] = [
    # -------------------------------------------------------------------------
    # 1. Open / Active Mainboard IPOs
    # -------------------------------------------------------------------------
    {
        "id": "varmora-granito",
        "name": "Varmora Granito Ltd",
        "symbol": "VARMORA",
        "category": "Mainboard",
        "ipo_type": "Mainboard",
        "tab_status": "open",
        "price_band": "₹140 - ₹148",
        "min_price": 140,
        "max_price": 148,
        "lot_size": 101,
        "min_investment": 14948,
        "issue_size_cr": 708.02,
        "fresh_issue_cr": 320.00,
        "ofs_cr": 388.02,
        "open_date": "22 Sep",
        "close_date": "24 Sep",
        "closing_display": "24 Sep",
        "allotment_date": "25 Sep",
        "listing_date": "29 Sep",
        "status": "Open (Bidding Active)",
        "action_type": "Apply",
        "action_label": "Apply",
        "gmp_inr": 28,
        "gmp_percent": 18.9,
        "subscription_x": 0.11,
        "qib_x": 0.05,
        "nii_x": 0.18,
        "retail_x": 0.14,
        "pe_ratio": 26.4,
        "sector_pe": 32.0,
        "verdict": "🟢 APPLY (Moderate Listing Gains & Brand Moat)",
        "conviction_score": 82,
        "pros": [
            "Leading Indian ceramic & vitrified tile manufacturer with nationwide distribution of 1,200+ dealers.",
            "Fresh issue funds dedicated to expansion into high-margin sanitaryware and bathware.",
            "Reasonable P/E valuation (26.4x) compared to peers like Kajaria Ceramics (44x)."
        ],
        "cons": [
            "Raw material gas and clay price fluctuations impact operating margins.",
            "Working capital intensity in dealer credit cycles."
        ],
        "recommendation_summary": "Favorable risk-reward for retail investors seeking 15-20% listing pop and mid-cap building materials play."
    },
    # -------------------------------------------------------------------------
    # 2. Pre-Apply / Upcoming Mainboard IPOs
    # -------------------------------------------------------------------------
    {
        "id": "armee-infotech",
        "name": "ArMee Infotech Ltd",
        "symbol": "ARMEE",
        "category": "Mainboard",
        "ipo_type": "Mainboard",
        "tab_status": "open",
        "price_band": "₹350 - ₹375",
        "min_price": 350,
        "max_price": 375,
        "lot_size": 40,
        "min_investment": 15000,
        "issue_size_cr": 300.00,
        "fresh_issue_cr": 300.00,
        "ofs_cr": 0.00,
        "open_date": "23 Sep",
        "close_date": "25 Sep",
        "closing_display": "25 Sep",
        "allotment_date": "28 Sep",
        "listing_date": "30 Sep",
        "status": "Pre-apply Open",
        "action_type": "Pre-apply",
        "action_label": "Pre-apply",
        "gmp_inr": 65,
        "gmp_percent": 17.3,
        "subscription_x": 0.0,
        "qib_x": 0.0,
        "nii_x": 0.0,
        "retail_x": 0.0,
        "pe_ratio": 21.8,
        "sector_pe": 28.5,
        "verdict": "🟢 STRONG APPLY (100% Fresh Issue IT Play)",
        "conviction_score": 88,
        "pros": [
            "100% fresh issue proceeds (no promoter offloading) scaling cloud infrastructure and system integration.",
            "Consistent 32% YoY revenue growth with high repeat enterprise client retention.",
            "Low debt-to-equity ratio (0.15) with robust return on equity (ROE > 22%)."
        ],
        "cons": [
            "Customer concentration with top 5 clients contributing ~42% of revenue.",
            "Tech talent wage inflation pressure."
        ],
        "recommendation_summary": "Strong candidate for pre-application with favorable listing gain buffer and solid growth fundamentals."
    },
    {
        "id": "swastika-infra",
        "name": "Swastika Infra Ltd",
        "symbol": "SWASTIK",
        "category": "Mainboard",
        "ipo_type": "Mainboard",
        "tab_status": "open",
        "price_band": "₹175 - ₹185",
        "min_price": 175,
        "max_price": 185,
        "lot_size": 80,
        "min_investment": 14800,
        "issue_size_cr": 195.00,
        "fresh_issue_cr": 160.00,
        "ofs_cr": 35.00,
        "open_date": "23 Sep",
        "close_date": "25 Sep",
        "closing_display": "25 Sep",
        "allotment_date": "28 Sep",
        "listing_date": "30 Sep",
        "status": "Pre-apply Open",
        "action_type": "Pre-apply",
        "action_label": "Pre-apply",
        "gmp_inr": 42,
        "gmp_percent": 22.7,
        "subscription_x": 0.0,
        "qib_x": 0.0,
        "nii_x": 0.0,
        "retail_x": 0.0,
        "pe_ratio": 16.5,
        "sector_pe": 24.0,
        "verdict": "🟢 APPLY (Government Infra Order Pipeline)",
        "conviction_score": 84,
        "pros": [
            "Order book of ₹1,420 Cr providing 3.5x revenue visibility over the next 24 months.",
            "Specialized EPC capability in highway bridges and dedicated freight corridors.",
            "Attractive IPO pricing with single-digit forward EV/EBITDA."
        ],
        "cons": [
            "Execution dependency on state government clearances and weather disruptions.",
            "Higher working capital days typical of infra EPC sector."
        ],
        "recommendation_summary": "Apply for listing gains supported by robust +22% GMP and multi-year order backlog."
    },
    {
        "id": "elevate-campuses",
        "name": "Elevate Campuses Ltd",
        "symbol": "ELEVATE",
        "category": "Mainboard",
        "ipo_type": "Mainboard",
        "tab_status": "open",
        "price_band": "₹280 - ₹295",
        "min_price": 280,
        "max_price": 295,
        "lot_size": 50,
        "min_investment": 14750,
        "issue_size_cr": 240.00,
        "fresh_issue_cr": 190.00,
        "ofs_cr": 50.00,
        "open_date": "23 Sep",
        "close_date": "25 Sep",
        "closing_display": "25 Sep",
        "allotment_date": "28 Sep",
        "listing_date": "30 Sep",
        "status": "Pre-apply Open",
        "action_type": "Pre-apply",
        "action_label": "Pre-apply",
        "gmp_inr": 55,
        "gmp_percent": 18.6,
        "subscription_x": 0.0,
        "qib_x": 0.0,
        "nii_x": 0.0,
        "retail_x": 0.0,
        "pe_ratio": 28.2,
        "sector_pe": 31.0,
        "verdict": "🟡 CAUTION / SELECTIVE APPLY",
        "conviction_score": 68,
        "pros": [
            "Student housing and modern campus infrastructure REIT-like annuity rental cash flows.",
            "High 94% occupancy across tier-1 university hubs in Bengaluru, Pune, and NCR."
        ],
        "cons": [
            "Asset-heavy balance sheet with significant debt servicing requirements.",
            "Regulatory guidelines on university campus accommodations."
        ],
        "recommendation_summary": "Selective apply for aggressive investors; moderate listing pop expected."
    },
    {
        "id": "adroit-industries",
        "name": "Adroit Industries Ltd",
        "symbol": "ADROIT",
        "category": "Mainboard",
        "ipo_type": "Mainboard",
        "tab_status": "open",
        "price_band": "₹230 - ₹242",
        "min_price": 230,
        "max_price": 242,
        "lot_size": 60,
        "min_investment": 14520,
        "issue_size_cr": 180.00,
        "fresh_issue_cr": 140.00,
        "ofs_cr": 40.00,
        "open_date": "23 Sep",
        "close_date": "25 Sep",
        "closing_display": "25 Sep",
        "allotment_date": "28 Sep",
        "listing_date": "30 Sep",
        "status": "Pre-apply Open",
        "action_type": "Pre-apply",
        "action_label": "Pre-apply",
        "gmp_inr": 35,
        "gmp_percent": 14.5,
        "subscription_x": 0.0,
        "qib_x": 0.0,
        "nii_x": 0.0,
        "retail_x": 0.0,
        "pe_ratio": 23.5,
        "sector_pe": 26.0,
        "verdict": "🟡 CAUTION",
        "conviction_score": 65,
        "pros": [
            "Precision auto component supplier for leading domestic 4-wheeler & commercial OEMs.",
            "Export expansion to European tier-1 auto assemblers."
        ],
        "cons": [
            "Auto cycle slowdown risks and steel raw material cost pass-through lag."
        ],
        "recommendation_summary": "Average listing upside; apply only if overall market sentiment remains bullish."
    },
    {
        "id": "a-one-steels",
        "name": "A-One Steels Ltd",
        "symbol": "AONESTEEL",
        "category": "Mainboard",
        "ipo_type": "Mainboard",
        "tab_status": "open",
        "price_band": "₹210 - ₹225",
        "min_price": 210,
        "max_price": 225,
        "lot_size": 66,
        "min_investment": 14850,
        "issue_size_cr": 210.00,
        "fresh_issue_cr": 180.00,
        "ofs_cr": 30.00,
        "open_date": "24 Sep",
        "close_date": "28 Sep",
        "closing_display": "28 Sep",
        "allotment_date": "29 Sep",
        "listing_date": "03 Oct",
        "status": "Pre-apply Open",
        "action_type": "Pre-apply",
        "action_label": "Pre-apply",
        "gmp_inr": 48,
        "gmp_percent": 21.3,
        "subscription_x": 0.0,
        "qib_x": 0.0,
        "nii_x": 0.0,
        "retail_x": 0.0,
        "pe_ratio": 15.2,
        "sector_pe": 22.0,
        "verdict": "🟢 APPLY (Value Steel Rebar Play)",
        "conviction_score": 80,
        "pros": [
            "High-grade TMT rebar manufacturer benefiting from government PM Awas Yojana & road capex.",
            "Fully integrated secondary steel smelting with captive solar power offsetting electricity cost."
        ],
        "cons": [
            "Cyclical commodity industry with pricing dictated by global scrap steel rates."
        ],
        "recommendation_summary": "Apply for listing gains supported by +21% GMP and low valuation multiple."
    },
    # -------------------------------------------------------------------------
    # 3. SME IPOs (High Demand / Last Day)
    # -------------------------------------------------------------------------
    {
        "id": "robokidz-eduventures",
        "name": "Robokidz Eduventures Ltd",
        "symbol": "ROBOKIDZ",
        "category": "SME",
        "ipo_type": "SME",
        "tab_status": "open",
        "is_last_day": True,
        "price_band": "₹100 - ₹106",
        "min_price": 100,
        "max_price": 106,
        "lot_size": 1200,
        "min_investment": 127200,
        "issue_size_cr": 31.09,
        "fresh_issue_cr": 31.09,
        "ofs_cr": 0.00,
        "open_date": "21 Sep",
        "close_date": "23 Sep",
        "closing_display": "23 Sep - Last day",
        "allotment_date": "24 Sep",
        "listing_date": "28 Sep",
        "status": "Open (Last Day Bidding)",
        "action_type": "Apply",
        "action_label": "Apply",
        "gmp_inr": 52,
        "gmp_percent": 49.1,
        "subscription_x": 67.21,
        "qib_x": 34.5,
        "nii_x": 88.4,
        "retail_x": 78.6,
        "pe_ratio": 18.5,
        "sector_pe": 28.0,
        "verdict": "🔥 HIGH ALPHA APPLY (SME STEM Robotics Leader)",
        "conviction_score": 90,
        "pros": [
            "Pioneer in STEM robotics and AI lab curriculum in 850+ private schools across India.",
            "Massive 67x subscription demand indicating blockbuster listing pop potential (+49% GMP).",
            "High operating margin (>28%) with negative working capital cash cycle."
        ],
        "cons": [
            "SME board liquidity risk with minimum trading lot of 1,200 shares.",
            "Dependence on school academic calendar procurement cycles."
        ],
        "recommendation_summary": "High-conviction apply for SME listing pop; expect 40-50% listing day surge."
    },
    {
        "id": "fx-multitech",
        "name": "FX Multitech Ltd",
        "symbol": "FXMULTI",
        "category": "SME",
        "ipo_type": "SME",
        "tab_status": "open",
        "is_last_day": True,
        "price_band": "₹140 - ₹148",
        "min_price": 140,
        "max_price": 148,
        "lot_size": 1000,
        "min_investment": 148000,
        "issue_size_cr": 28.50,
        "fresh_issue_cr": 28.50,
        "ofs_cr": 0.00,
        "open_date": "21 Sep",
        "close_date": "23 Sep",
        "closing_display": "23 Sep - Last day",
        "allotment_date": "24 Sep",
        "listing_date": "28 Sep",
        "status": "Open (Last Day)",
        "action_type": "Apply",
        "action_label": "Apply",
        "gmp_inr": 12,
        "gmp_percent": 8.1,
        "subscription_x": 0.43,
        "qib_x": 0.10,
        "nii_x": 0.45,
        "retail_x": 0.74,
        "pe_ratio": 34.0,
        "sector_pe": 26.0,
        "verdict": "🔴 STRICT AVOID (Overvalued & Weak Demand)",
        "conviction_score": 35,
        "pros": [
            "Industrial polymer packaging supplier."
        ],
        "cons": [
            "Sub-par subscription demand (0.43x on final day) risks listing discount.",
            "High debt burden with promoter pledge history.",
            "Stretched P/E multiple (34x) vs sector average (26x)."
        ],
        "recommendation_summary": "Avoid. Low subscription and weak GMP increase downside risk on listing day."
    },
    # -------------------------------------------------------------------------
    # 4. Closed / Recently Listed Blockbusters (Historical Audit & Allotment)
    # -------------------------------------------------------------------------
    {
        "id": "bajaj-housing",
        "name": "Bajaj Housing Finance Ltd",
        "symbol": "BAJAJHFL",
        "category": "Mainboard",
        "ipo_type": "Mainboard",
        "tab_status": "closed",
        "price_band": "₹66 - ₹70",
        "min_price": 66,
        "max_price": 70,
        "lot_size": 214,
        "min_investment": 14980,
        "issue_size_cr": 6560.00,
        "fresh_issue_cr": 3560.00,
        "ofs_cr": 3000.00,
        "open_date": "09 Sep",
        "close_date": "11 Sep",
        "closing_display": "11 Sep (Listed)",
        "allotment_date": "12 Sep",
        "listing_date": "16 Sep",
        "status": "Closed (Listed @ ₹150 / +114%)",
        "action_type": "Allotment",
        "action_label": "View Allotment",
        "gmp_inr": 82,
        "gmp_percent": 117.1,
        "subscription_x": 67.43,
        "qib_x": 222.0,
        "nii_x": 43.2,
        "retail_x": 7.4,
        "pe_ratio": 29.5,
        "sector_pe": 34.2,
        "verdict": "🌟 BLOCKBUSTER (Listed @ 114% Gain)",
        "conviction_score": 96,
        "pros": ["Elite Bajaj pedigree", "Pristine asset quality", "Delivered 114% day-1 returns."],
        "cons": ["Hold for multi-year compounding."],
        "recommendation_summary": "Allotment successful. Hold core position for long-term wealth compounder."
    },
    {
        "id": "premier-energies",
        "name": "Premier Energies Ltd",
        "symbol": "PREMIERENE",
        "category": "Mainboard",
        "ipo_type": "Mainboard",
        "tab_status": "closed",
        "price_band": "₹427 - ₹450",
        "min_price": 427,
        "max_price": 450,
        "lot_size": 33,
        "min_investment": 14850,
        "issue_size_cr": 2830.00,
        "fresh_issue_cr": 1291.00,
        "ofs_cr": 1539.00,
        "open_date": "27 Aug",
        "close_date": "29 Aug",
        "closing_display": "29 Aug (Listed)",
        "allotment_date": "30 Aug",
        "listing_date": "03 Sep",
        "status": "Closed (Listed @ ₹991 / +120%)",
        "action_type": "Allotment",
        "action_label": "View Allotment",
        "gmp_inr": 540,
        "gmp_percent": 120.0,
        "subscription_x": 75.00,
        "qib_x": 216.0,
        "nii_x": 50.0,
        "retail_x": 7.6,
        "pe_ratio": 42.0,
        "sector_pe": 50.0,
        "verdict": "🌟 BLOCKBUSTER (Listed @ 120% Gain)",
        "conviction_score": 95,
        "pros": ["India's second-largest integrated solar cell & module manufacturer."],
        "cons": ["Lock-in expiration watchlist."],
        "recommendation_summary": "Listed with 120% gain. Book partial profits and trail stop-loss."
    },
    # -------------------------------------------------------------------------
    # 5. Upcoming Mega Issues
    # -------------------------------------------------------------------------
    {
        "id": "ntpc-green",
        "name": "NTPC Green Energy Ltd",
        "symbol": "NTPCGREEN",
        "category": "Mainboard",
        "ipo_type": "Mainboard",
        "tab_status": "upcoming",
        "price_band": "₹102 - ₹108",
        "min_price": 102,
        "max_price": 108,
        "lot_size": 138,
        "min_investment": 14904,
        "issue_size_cr": 10000.00,
        "fresh_issue_cr": 10000.00,
        "ofs_cr": 0.00,
        "open_date": "14 Oct",
        "close_date": "18 Oct",
        "closing_display": "18 Oct",
        "allotment_date": "21 Oct",
        "listing_date": "24 Oct",
        "status": "Upcoming Mega Issue",
        "action_type": "Notify",
        "action_label": "Notify Me",
        "gmp_inr": 28,
        "gmp_percent": 25.9,
        "subscription_x": 0.0,
        "qib_x": 0.0,
        "nii_x": 0.0,
        "retail_x": 0.0,
        "pe_ratio": 48.0,
        "sector_pe": 55.0,
        "verdict": "🟢 APPLY (Sovereign Clean Energy Transition)",
        "conviction_score": 88,
        "pros": [
            "Strong sovereign Maharatna parentage with massive government clean energy pipeline.",
            "100% fresh issue proceeds dedicated to solar & wind scaling."
        ],
        "cons": ["Capital intensive execution."],
        "recommendation_summary": "Top upcoming sovereign green transition IPO."
    },
    {
        "id": "swiggy",
        "name": "Swiggy Ltd",
        "symbol": "SWIGGY",
        "category": "Mainboard",
        "ipo_type": "Mainboard",
        "tab_status": "upcoming",
        "price_band": "₹371 - ₹390",
        "min_price": 371,
        "max_price": 390,
        "lot_size": 38,
        "min_investment": 14820,
        "issue_size_cr": 11327.00,
        "fresh_issue_cr": 3750.00,
        "ofs_cr": 7577.00,
        "open_date": "06 Nov",
        "close_date": "08 Nov",
        "closing_display": "08 Nov",
        "allotment_date": "11 Nov",
        "listing_date": "13 Nov",
        "status": "Upcoming Mega Tech",
        "action_type": "Notify",
        "action_label": "Notify Me",
        "gmp_inr": 18,
        "gmp_percent": 4.6,
        "subscription_x": 0.0,
        "qib_x": 0.0,
        "nii_x": 0.0,
        "retail_x": 0.0,
        "pe_ratio": -45.0,
        "sector_pe": 72.0,
        "verdict": "🟡 CAUTION / HIGH RISK (Quick Commerce Burn)",
        "conviction_score": 62,
        "pros": [
            "Duopoly in Indian online food delivery and rapid Instamart quick-commerce scaling."
        ],
        "cons": [
            "Intense price competition vs Zomato (Blinkit) and Zepto causing cash burn."
        ],
        "recommendation_summary": "Caution. High quick-commerce cash burn limits short-term listing upside."
    }
]


class IPOService:
    def __init__(self):
        self.applied_ipos: List[Dict[str, Any]] = [
            {
                "application_id": "IPO-2026-BAJAJ-7821",
                "ipo_id": "bajaj-housing",
                "name": "Bajaj Housing Finance Ltd",
                "symbol": "BAJAJHFL",
                "category": "Mainboard",
                "lots": 1,
                "shares": 214,
                "bid_price": 70,
                "amount_blocked": 14980,
                "applied_date": "10 Sep 2026",
                "status": "Allotted (214 Shares)",
                "upi_id": "user@okhdfcbank",
                "pnl_inr": "+₹17,120",
                "pnl_percent": "+114.3%"
            }
        ]

    def get_all_ipos(self) -> List[Dict[str, Any]]:
        return IPO_CATALOG

    def get_ipo_by_id(self, ipo_id: str) -> Optional[Dict[str, Any]]:
        for ipo in IPO_CATALOG:
            if ipo["id"] == ipo_id or ipo["symbol"].lower() == ipo_id.lower():
                return ipo
        return None

    def get_applied_ipos(self) -> List[Dict[str, Any]]:
        return self.applied_ipos

    def apply_for_ipo(self, ipo_id: str, lots: int = 1, upi_id: str = "user@okhdfcbank", cut_off: bool = True) -> Dict[str, Any]:
        ipo = self.get_ipo_by_id(ipo_id)
        if not ipo:
            return {"success": False, "message": "IPO not found"}

        lot_size = ipo.get("lot_size", 50)
        total_shares = lots * lot_size
        price = ipo.get("max_price", 100) if cut_off else ipo.get("min_price", 100)
        amount = total_shares * price

        import random
        app_num = f"IPO-2026-{ipo.get('symbol', 'APP')}-{random.randint(1000, 9999)}"
        
        record = {
            "application_id": app_num,
            "ipo_id": ipo["id"],
            "name": ipo["name"],
            "symbol": ipo["symbol"],
            "category": ipo.get("category", "Mainboard"),
            "lots": lots,
            "shares": total_shares,
            "bid_price": price,
            "amount_blocked": amount,
            "applied_date": "23 Sep 2026",
            "status": "Mandate Submitted (Pending Allotment)",
            "upi_id": upi_id,
            "closing_date": ipo.get("close_date", "25 Sep"),
            "allotment_date": ipo.get("allotment_date", "28 Sep")
        }

        # Check if already applied
        existing = [a for a in self.applied_ipos if a["ipo_id"] == ipo["id"]]
        if existing:
            existing[0].update(record)
        else:
            self.applied_ipos.insert(0, record)

        return {
            "success": True,
            "application_id": app_num,
            "message": f"Application for {lots} lot(s) ({total_shares} shares) of {ipo['name']} submitted successfully. UPI mandate of ₹{amount:,.2f} requested to {upi_id}.",
            "record": record
        }

    def get_active_and_upcoming_ipos(self) -> List[Dict[str, Any]]:
        return [i for i in IPO_CATALOG if i.get("tab_status") in ("open", "upcoming")]

    def get_ipo_recommendation_summary(self) -> Dict[str, Any]:
        total = len(IPO_CATALOG)
        strong_apply = len([i for i in IPO_CATALOG if "STRONG APPLY" in i["verdict"] or "HIGH ALPHA" in i["verdict"]])
        apply_lt = len([i for i in IPO_CATALOG if "APPLY" in i["verdict"] and "STRONG" not in i["verdict"]])
        caution = len([i for i in IPO_CATALOG if "CAUTION" in i["verdict"]])
        avoid = len([i for i in IPO_CATALOG if "AVOID" in i["verdict"]])
        return {
            "total_ipos": total,
            "strong_apply_count": strong_apply,
            "apply_longterm_count": apply_lt,
            "caution_count": caution,
            "avoid_count": avoid,
            "applied_count": len(self.applied_ipos),
            "high_gmp_picks": [i["name"] for i in IPO_CATALOG if i.get("gmp_percent", 0) >= 30]
        }


ipo_service = IPOService()


