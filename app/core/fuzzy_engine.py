"""
Fuzzy Logic Probability Engine

Implements a Sugeno-type fuzzy inference system for sports betting predictions.

TODO: INSERT YOUR FUZZY LOGIC IMPLEMENTATION HERE
- Define membership functions for input variables
- Create fuzzy rule base
- Implement Sugeno inference
- Defuzzification
"""

class FuzzyEngine:
    def __init__(self):
        self.membership_funcs = self._init_membership_functions()
    
    def _init_membership_functions(self):
        """Initialize triangular membership functions for inputs"""
        return {
            "goals": {
                "low": (0.0, 0.5, 1.5),
                "medium": (1.0, 1.5, 2.5),
                "high": (2.0, 3.0, 5.0)
            },
            "implied_prob": {
                "low": (0.0, 0.25, 0.45),
                "medium": (0.35, 0.50, 0.65),
                "high": (0.55, 0.75, 1.0)
            }
        }
    
    def triangular_membership(self, x: float, a: float, b: float, c: float) -> float:
        """Triangular membership function: returns degree of membership"""
        if x <= a or x >= c:
            return 0.0
        if a < x <= b:
            return (x - a) / (b - a) if b > a else 0.0
        return (c - x) / (c - b) if c > b else 0.0
    
    def fuzzify(self, home_goals: float, away_goals: float, odds_home: float, odds_draw: float, odds_away: float):
        """Convert crisp inputs to fuzzy sets"""
        # Calculate implied probability from odds
        total_odds = 1/odds_home + 1/odds_draw + 1/odds_away
        implied_prob_home = (1/odds_home) / total_odds
        
        # Fuzzify home goals
        home_low = self.triangular_membership(home_goals, 0.0, 0.5, 1.5)
        home_med = self.triangular_membership(home_goals, 1.0, 1.5, 2.5)
        home_high = self.triangular_membership(home_goals, 2.0, 3.0, 5.0)
        
        # Fuzzify away goals
        away_low = self.triangular_membership(away_goals, 0.0, 0.5, 1.5)
        away_med = self.triangular_membership(away_goals, 1.0, 1.5, 2.5)
        away_high = self.triangular_membership(away_goals, 2.0, 3.0, 5.0)
        
        # Fuzzify implied probability
        prob_low = self.triangular_membership(implied_prob_home, 0.0, 0.25, 0.45)
        prob_med = self.triangular_membership(implied_prob_home, 0.35, 0.50, 0.65)
        prob_high = self.triangular_membership(implied_prob_home, 0.55, 0.75, 1.0)
        
        return {
            "home_goals": {"low": home_low, "med": home_med, "high": home_high},
            "away_goals": {"low": away_low, "med": away_med, "high": away_high},
            "prob": {"low": prob_low, "med": prob_med, "high": prob_high},
            "implied_prob": implied_prob_home
        }
    
    def apply_rules(self, fuzzy_sets):
        """Fuzzy rules engine - Sugeno style"""
        home_goals = fuzzy_sets["home_goals"]
        away_goals = fuzzy_sets["away_goals"]
        prob = fuzzy_sets["prob"]
        
        # Sugeno consequents (crisp outputs)
        consequents = {
            "very_high": 0.85,
            "high": 0.70,
            "medium": 0.50,
            "low": 0.30,
            "very_low": 0.15
        }
        
        # Rule strengths (antecedent weights)
        rule_fire = {}
        
        # Rule 1: If home_goals HIGH AND away_goals LOW THEN very_high
        rule_fire["very_high"] = min(home_goals["high"], away_goals["low"])
        
        # Rule 2: If home_goals HIGH AND away_goals MED THEN high
        rule_fire["high"] = max(
            min(home_goals["high"], away_goals["med"]),
            min(home_goals["med"], away_goals["low"]),
            min(prob["high"], home_goals["med"])
        )
        
        # Rule 3: If home_goals MED THEN medium
        rule_fire["medium"] = max(
            home_goals["med"],
            min(prob["med"], home_goals["med"])
        )
        
        # Rule 4: If away_goals HIGH THEN low
        rule_fire["low"] = min(away_goals["high"], 1 - home_goals["high"])
        
        # Rule 5: If away_goals HIGH AND home_goals LOW THEN very_low
        rule_fire["very_low"] = min(away_goals["high"], home_goals["low"])
        
        return rule_fire, consequents
    
    def defuzzify(self, rule_fire, consequents):
        """Sugeno defuzzification (weighted average)"""
        numerator = sum(rule_fire[rule] * consequents[rule] for rule in rule_fire)
        denominator = sum(rule_fire.values())
        
        if denominator == 0:
            return 0.5
        
        return numerator / denominator

_fuzzy_engine = FuzzyEngine()

def calculate_probability(
    home_goals_avg: float,
    away_goals_avg: float,
    odds_home: float,
    odds_draw: float,
    odds_away: float
) -> tuple[float, float, float]:
    """
    Calculate probabilities for all three outcomes using fuzzy logic
    
    Args:
        home_goals_avg: Average goals scored by home team
        away_goals_avg: Average goals scored by away team
        odds_home: Market odds for home win
        odds_draw: Market odds for draw
        odds_away: Market odds for away win
    
    Returns:
        Tuple of (p_home, p_draw, p_away) fuzzy probabilities
    """
    
    # Fuzzification
    fuzzy_sets = _fuzzy_engine.fuzzify(home_goals_avg, away_goals_avg, odds_home, odds_draw, odds_away)
    
    # Rule evaluation
    rule_fire, consequents = _fuzzy_engine.apply_rules(fuzzy_sets)
    
    # Defuzzification for home win
    p_home = _fuzzy_engine.defuzzify(rule_fire, consequents)
    
    # Calculate away probability (reversed logic)
    goal_diff_away = away_goals_avg - home_goals_avg
    p_away_base = max(0.0, min(1.0, 0.5 + (goal_diff_away * 0.15)))
    
    # Calculate implied probabilities from odds
    total_odds_inv = 1/odds_home + 1/odds_draw + 1/odds_away
    implied_home = (1/odds_home) / total_odds_inv
    implied_draw = (1/odds_draw) / total_odds_inv
    implied_away = (1/odds_away) / total_odds_inv
    
    # Blend fuzzy and implied (60% fuzzy, 40% market)
    p_home_final = 0.6 * p_home + 0.4 * implied_home
    p_away_final = 0.6 * p_away_base + 0.4 * implied_away
    p_draw_final = 0.6 * max(0.0, 1.0 - p_home - p_away_base) + 0.4 * implied_draw
    
    # Normalize to sum to 1.0
    total = p_home_final + p_draw_final + p_away_final
    if total > 0:
        p_home_final /= total
        p_draw_final /= total
        p_away_final /= total
    else:
        p_home_final = p_draw_final = p_away_final = 1.0 / 3.0
    
    return (
        max(0.0, min(1.0, p_home_final)),
        max(0.0, min(1.0, p_draw_final)),
        max(0.0, min(1.0, p_away_final))
    )
