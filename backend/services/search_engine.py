"""
AlphaLens Financial Natural Language & Semantic Search Engine
Translates human financial questions into structured queries, evidence analyses,
stock comparisons, portfolio stress tests, and AI customer buy/avoid recommendations.
"""

import re
from typing import Dict, Any, List
from backend.services.advisory_engine import advisory_engine


class SearchEngine:
    def __init__(self):
        pass

    def process_query(self, query: str, stock_data: Dict[str, Any], portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parses natural language query and dispatches to appropriate intelligence handler."""
        q = query.strip().lower()

        # 1. 'Should I buy / avoid [STOCK]?' or 'Is [STOCK] good to buy?'
        should_buy_match = re.search(r"(?:should i buy|can i buy|is it good to buy|is (\w+) a buy|buy or avoid|recommendation on) (\w+)", q)
        if should_buy_match:
            cand = (should_buy_match.group(2) or should_buy_match.group(1)).upper()
            matched_ticker = self._find_ticker(cand, stock_data)
            if matched_ticker:
                return self._handle_stock_advisory_query(matched_ticker, stock_data[matched_ticker])

        # 2. 'Which stocks should I buy?' / 'Best stocks to buy' / 'Top picks'
        buy_phrases = [
            "which stocks should i buy", "which stock should i buy", "which stock to buy",
            "which stocks to buy", "stocks to buy", "stock to buy", "what should i buy",
            "what to buy", "best stocks to buy", "best stocks", "top buys", "buy picks",
            "recommendations", "suggest stocks", "top picks", "what stock should i buy"
        ]
        if any(w in q for w in buy_phrases):
            return self._handle_buy_suggestions(stock_data)

        # 3. 'Which stocks should I avoid?' / 'Stocks to avoid' / 'High risk stocks'
        avoid_phrases = [
            "which stocks should i avoid", "which stock should i avoid", "which stock to avoid",
            "which stocks to avoid", "stocks to avoid", "stock to avoid", "what should i avoid",
            "what to avoid", "risky stocks", "high risk stocks", "don't buy", "dont buy",
            "stocks to sell", "avoid stocks"
        ]
        if any(w in q for w in avoid_phrases):
            return self._handle_avoid_suggestions(stock_data)

        # 4. 'Why is [STOCK] falling / rising / moving?'
        why_match = re.search(r"why is (\w+)(?: falling| rising| moving| down| up)?", q)
        if why_match:
            cand = why_match.group(1).upper()
            matched_ticker = self._find_ticker(cand, stock_data)
            if matched_ticker:
                return self._handle_why_stock(matched_ticker, stock_data[matched_ticker])

        # 5. 'Compare [STOCK1] and [STOCK2]'
        compare_match = re.search(r"compare (\w+)(?: and | vs | with )(\w+)", q)
        if compare_match:
            t1 = self._find_ticker(compare_match.group(1).upper(), stock_data)
            t2 = self._find_ticker(compare_match.group(2).upper(), stock_data)
            if t1 and t2:
                return self._handle_comparison(t1, t2, stock_data)

        # 6. Portfolio questions
        if "portfolio" in q and ("movement" in q or "biggest" in q or "moved" in q):
            return self._handle_portfolio_movement(portfolio_data)
        
        if "nifty falls 5%" in q or "nifty drops" in q or "market crash" in q:
            return self._handle_portfolio_scenario(portfolio_data, "nifty_drop_5pct")

        if "crude" in q or "oil" in q:
            return self._handle_portfolio_scenario(portfolio_data, "crude_oil_spike_10pct")

        # 7. Multi-factor screener queries: 'momentum', 'sentiment', 'valuation', 'debt'
        if "momentum" in q or "sentiment" in q or "valuation" in q or "large indian" in q or "screen" in q:
            return self._handle_factor_search(q, stock_data)

        # 8. Direct ticker lookup fallback
        direct_ticker = self._find_ticker(query.strip().upper(), stock_data)
        if direct_ticker:
            return self._handle_stock_advisory_query(direct_ticker, stock_data[direct_ticker])

        # 9. General Market Summary fallback
        return self._handle_general_market_overview(stock_data)

    def _find_ticker(self, term: str, stock_data: Dict[str, Any]) -> str:
        term = term.upper().strip()
        if term in stock_data:
            return term
        # Fuzzy match company names
        for ticker, data in stock_data.items():
            name = data.get("name", "").upper()
            if term == ticker or term in name or name in term:
                return ticker
        return None

    def _handle_stock_advisory_query(self, ticker: str, stock: Dict[str, Any]) -> Dict[str, Any]:
        """Provides instant Buy/Avoid verdict for a searched stock."""
        advisory = stock.get("advisory") or advisory_engine.evaluate_advisory(stock)
        verdict = advisory.get("verdict", "HOLD / WATCH")
        badge_class = advisory.get("badge_class", "badge-hold")
        targets = advisory.get("targets", {})
        
        return {
            "type": "ADVISORY_INSIGHT",
            "title": f"{stock.get('name')} ({ticker}) — Customer Advisory",
            "ticker": ticker,
            "verdict": verdict,
            "badge_class": badge_class,
            "conviction": f"{advisory.get('conviction_score', 75)}% Conviction",
            "headline": f"AI Guidance: {verdict} — {advisory.get('action_summary')}",
            "suitability": advisory.get("suitability"),
            "targets": targets,
            "why_buy": advisory.get("why_buy_reasons", [])[:2],
            "why_avoid": advisory.get("why_avoid_warnings", [])[:2],
            "action_text": f"Open full analysis & charts for {ticker} →",
            "action_ticker": ticker
        }

    def _handle_buy_suggestions(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        recs = advisory_engine.get_categorized_recommendations(stock_data)
        top_buys = recs.get("top_buys", [])[:4]
        
        return {
            "type": "TOP_BUYS_LIST",
            "title": "🎯 AI Top Buy Recommendations for Today",
            "headline": "High-conviction equities exhibiting strong trend alignment, positive volume, and optimal momentum.",
            "picks": [
                {
                    "ticker": b["ticker"],
                    "name": b["name"],
                    "price": f"₹{b['current_price']:,.1f}",
                    "verdict": b["verdict"],
                    "conviction": f"{b['conviction_score']}%",
                    "entry_zone": b["targets"]["entry_zone"],
                    "target": f"{b['targets']['target_1']} ({b['targets']['target_1_upside']})",
                    "stop_loss": b["targets"]["stop_loss"],
                    "reason": b["why_buy_reasons"][0] if b["why_buy_reasons"] else "Strong technical structure"
                }
                for b in top_buys
            ],
            "action_text": "Explore All AI Recommendations in Advisory Hub →"
        }

    def _handle_avoid_suggestions(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        recs = advisory_engine.get_categorized_recommendations(stock_data)
        avoids = recs.get("stocks_to_avoid", [])[:4]
        
        return {
            "type": "STOCKS_TO_AVOID_LIST",
            "title": "⚠️ Stocks to Avoid / High Risk Caution List",
            "headline": "Equities currently exhibiting technical breakdown, extreme overbought exhaustion, or unfavorable risk-reward.",
            "picks": [
                {
                    "ticker": a["ticker"],
                    "name": a["name"],
                    "price": f"₹{a['current_price']:,.1f}",
                    "verdict": a["verdict"],
                    "conviction": f"{a['conviction_score']}%",
                    "warning": a["why_avoid_warnings"][0] if a["why_avoid_warnings"] else "Technical breakdown below support",
                    "alternative": a.get("alternative_suggestion") or "Consider defensive bluechips with RSI in 50-60 range."
                }
                for a in avoids
            ],
            "action_text": "Review Full Risk Breakdown in Advisory Hub →"
        }

    def _handle_why_stock(self, ticker: str, stock: Dict[str, Any]) -> Dict[str, Any]:
        chg = stock.get("change_1d_pct", 0.0)
        direction_word = "up" if chg >= 0 else "down"
        evidence = stock.get("evidence", {})
        outlook = stock.get("model_outlook", {})
        risk = stock.get("risk", {})
        advisory = stock.get("advisory") or advisory_engine.evaluate_advisory(stock)

        factors = [
            f"01  Sector & Market Trend: {evidence.get('market_trend', 'Neutral')} broad environment",
            f"02  FinBERT News Sentiment: {evidence.get('news_sentiment', 'Neutral')} institutional coverage",
            f"03  Volume Profile: {evidence.get('volume', 'Average')} relative liquidity"
        ]

        return {
            "type": "STOCK_EXPLANATION",
            "title": f"{stock.get('name')} ({ticker})",
            "ticker": ticker,
            "headline": f"{ticker} is {direction_word} {abs(chg):.2f}% today. Advisory Verdict: {advisory.get('verdict')}",
            "factors": factors,
            "technical_trend": evidence.get("trend", "Neutral"),
            "news_sentiment": evidence.get("news_sentiment", "Neutral"),
            "model_outlook": {
                "direction": outlook.get("direction", "Positive"),
                "probability": f"{outlook.get('probability_percent', 70)}% probability",
                "horizon": outlook.get("horizon", "Next trading session")
            },
            "risk_level": risk.get("risk_level", "Medium"),
            "action_text": f"View detailed analysis for {ticker} →",
            "action_ticker": ticker
        }

    def _handle_comparison(self, t1: str, t2: str, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        s1 = stock_data[t1]
        s2 = stock_data[t2]
        adv1 = s1.get("advisory") or advisory_engine.evaluate_advisory(s1)
        adv2 = s2.get("advisory") or advisory_engine.evaluate_advisory(s2)

        comparison_table = [
            {"attribute": "Current Price", "val1": f"₹{s1.get('price'):,}", "val2": f"₹{s2.get('price'):,}"},
            {"attribute": "Today's Change", "val1": f"{s1.get('change_1d_pct'):+.2f}%", "val2": f"{s2.get('change_1d_pct'):+.2f}%"},
            {"attribute": "Advisory Verdict", "val1": adv1.get("verdict"), "val2": adv2.get("verdict")},
            {"attribute": "Conviction Score", "val1": f"{adv1.get('conviction_score')}%", "val2": f"{adv2.get('conviction_score')}%"},
            {"attribute": "Target 1 (Upside)", "val1": adv1.get("targets", {}).get("target_1_upside", "+10%"), "val2": adv2.get("targets", {}).get("target_1_upside", "+10%")},
            {"attribute": "Stop Loss Risk", "val1": adv1.get("targets", {}).get("stop_loss_risk", "-5%"), "val2": adv2.get("targets", {}).get("stop_loss_risk", "-5%")},
            {"attribute": "Trend", "val1": s1.get("evidence", {}).get("trend", "Neutral"), "val2": s2.get("evidence", {}).get("trend", "Neutral")},
            {"attribute": "Model Outlook", "val1": f"{s1.get('model_outlook', {}).get('probability_percent', 70)}% {s1.get('model_outlook', {}).get('direction')}", "val2": f"{s2.get('model_outlook', {}).get('probability_percent', 60)}% {s2.get('model_outlook', {}).get('direction')}"},
        ]

        better = t1 if adv1.get("conviction_score", 0) >= adv2.get("conviction_score", 0) else t2
        return {
            "type": "COMPARISON",
            "title": f"Head-to-Head: {s1.get('name')} vs {s2.get('name')}",
            "ticker1": t1,
            "ticker2": t2,
            "horizon": "Next 5 to 20 trading sessions",
            "comparison_table": comparison_table,
            "takeaway": f"AI Recommendation favors {better} ({adv1.get('verdict') if better == t1 else adv2.get('verdict')}) based on higher conviction score and superior risk-reward profile."
        }

    def _handle_portfolio_movement(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        holdings = portfolio_data.get("holdings", [])
        sorted_h = sorted(holdings, key=lambda x: abs(x.get("today_pnl", 0)), reverse=True)
        top = sorted_h[0] if sorted_h else None

        return {
            "type": "PORTFOLIO_INSIGHT",
            "title": "Portfolio Movement Breakdown",
            "headline": f"Your portfolio moved {portfolio_data.get('today_pnl_formatted', '0')} ({portfolio_data.get('today_pnl_pct', 0):+.2f}%) today.",
            "primary_driver": f"The largest single contributor was {top['name']} ({top['ticker']}) with a {top['today_pnl']:+,.0f} P&L change ({top['today_change_pct']:+.2f}%)." if top else "Balanced market action.",
            "factors": [
                f"01  {top['ticker'] if top else 'Holdings'} price action accounted for key portfolio movement.",
                "02  Sector exposure experienced moderate relative strength.",
                "03  Portfolio Beta provided consistent alignment with benchmark gains."
            ]
        }

    def _handle_portfolio_scenario(self, portfolio_data: Dict[str, Any], scenario_key: str) -> Dict[str, Any]:
        val = portfolio_data.get("total_value", 284320.0)
        from backend.services.risk_engine import risk_engine
        scenario = risk_engine.simulate_scenario(scenario_key, val)

        return {
            "type": "SCENARIO_ANALYSIS",
            "title": f"Scenario Stress Test: {scenario['title']}",
            "headline": f"Estimated Portfolio Impact: {scenario['expected_impact_pct']:+.2f}% ({scenario['expected_impact_inr']:+,.0f})",
            "description": scenario["description"],
            "sector_breakdown": scenario["sector_impacts"],
            "recommended_action": scenario["recommended_action"]
        }

    def _handle_factor_search(self, query: str, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        results = []
        for ticker, s in stock_data.items():
            ev = s.get("evidence", {})
            fund = s.get("fundamentals", {})
            out = s.get("model_outlook", {})
            risk = s.get("risk", {})
            adv = s.get("advisory") or advisory_engine.evaluate_advisory(s)

            match_score = 0
            if "momentum" in query and ev.get("momentum") == "Strong":
                match_score += 3
            if "sentiment" in query and ev.get("news_sentiment") == "Positive":
                match_score += 2
            if "valuation" in query or "low pe" in query:
                pe = float(fund.get("pe_ratio", 30))
                if pe < 25.0:
                    match_score += 3
            if "low debt" in query or "debt" in query:
                de = float(fund.get("debt_equity", 1.0))
                if de < 0.5:
                    match_score += 2
            if adv.get("verdict") in ["STRONG BUY", "ACCUMULATE / BUY"]:
                match_score += 2

            results.append({
                "ticker": ticker,
                "name": s.get("name"),
                "sector": s.get("sector"),
                "price": f"₹{s.get('price'):,}",
                "momentum": ev.get("momentum", "Moderate"),
                "sentiment": ev.get("news_sentiment", "Neutral"),
                "valuation": "Attractive" if float(fund.get("pe_ratio", 30)) < 22 else "Moderate",
                "risk": risk.get("risk_level", "Medium"),
                "verdict": adv.get("verdict"),
                "score": match_score
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        top_matches = results[:5]

        return {
            "type": "SCREENER_MATCHES",
            "title": "Smart Factor Screener Results",
            "query_interpreted": "Criteria: Large Indian equities matching multi-factor momentum, sentiment, and risk constraints",
            "matches": top_matches
        }

    def _handle_general_market_overview(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "MARKET_OVERVIEW",
            "title": "Market Intelligence Query",
            "headline": "Search Indian equities, companies, or ask for AI Buy/Avoid advice.",
            "suggestions": [
                "Which stocks should I buy today?",
                "Which stocks should I avoid right now?",
                "Should I buy Suzlon or Tata Motors?",
                "Why is TCS falling?",
                "Find stocks with strong momentum but low debt"
            ]
        }


search_engine = SearchEngine()
