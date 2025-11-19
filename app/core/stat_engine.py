"""
Statistical Probability Engine

Implements statistical models for win probability estimation.

TODO: INSERT YOUR STATISTICAL MODEL HERE
- Poisson distribution for goal modeling
- Elo ratings
- Dixon-Coles model
- Or your custom statistical approach
"""

import math

def _poisson_probability(k: float, lambda_: float) -> float:
    """Calculate Poisson probability P(X=k)"""
    if lambda_ <= 0:
        return 0.0
    return (math.exp(-lambda_) * (lambda_ ** k)) / math.factorial(int(k))

def _calculate_home_advantage() -> float:
    """Home advantage factor (typical ~1.15 multiplier on goals)"""
    return 1.15

def calculate_probability(
    home_goals_avg: float,
    away_goals_avg: float,
    home_win_rate: float,
    away_win_rate: float
) -> tuple[float, float, float]:
    """
    Calculate probabilities for all three outcomes using statistical methods
    
    Args:
        home_goals_avg: Average goals scored by home team
        away_goals_avg: Average goals scored by away team
        home_win_rate: Historical win rate for home team
        away_win_rate: Historical win rate for away team
    
    Returns:
        Tuple of (p_home, p_draw, p_away) probabilities
    """
    
    # Ensure valid inputs
    home_goals_avg = max(0.1, min(home_goals_avg, 5.0))
    away_goals_avg = max(0.1, min(away_goals_avg, 5.0))
    home_win_rate = max(0.01, min(home_win_rate, 0.99))
    away_win_rate = max(0.01, min(away_win_rate, 0.99))
    
    # Apply home advantage to expected goals
    home_advantage = _calculate_home_advantage()
    adj_home_goals = home_goals_avg * home_advantage
    
    # Calculate all outcomes using Poisson
    p_home_poisson = 0.0
    p_draw_poisson = 0.0
    p_away_poisson = 0.0
    
    for home_goals in range(6):
        p_home = _poisson_probability(home_goals, adj_home_goals)
        
        for away_goals in range(6):
            p_away = _poisson_probability(away_goals, away_goals_avg)
            
            if home_goals > away_goals:
                p_home_poisson += p_home * p_away
            elif home_goals == away_goals:
                p_draw_poisson += p_home * p_away
            else:
                p_away_poisson += p_home * p_away
    
    # Blend with historical win rates (60-40 split)
    draw_rate = max(0.1, 1.0 - home_win_rate - away_win_rate)
    p_home_hybrid = 0.6 * p_home_poisson + 0.4 * home_win_rate
    p_draw_hybrid = 0.6 * p_draw_poisson + 0.4 * draw_rate
    p_away_hybrid = 0.6 * p_away_poisson + 0.4 * away_win_rate
    
    # Normalize to sum to 1.0
    total = p_home_hybrid + p_draw_hybrid + p_away_hybrid
    if total > 0:
        p_home_hybrid /= total
        p_draw_hybrid /= total
        p_away_hybrid /= total
    else:
        p_home_hybrid = p_draw_hybrid = p_away_hybrid = 1.0 / 3.0
    
    # Apply market skepticism adjustment (regress towards uniform 1/3)
    p_home_final = 0.7 * p_home_hybrid + 0.3 * (1.0 / 3.0)
    p_draw_final = 0.7 * p_draw_hybrid + 0.3 * (1.0 / 3.0)
    p_away_final = 0.7 * p_away_hybrid + 0.3 * (1.0 / 3.0)
    
    return (
        max(0.0, min(1.0, p_home_final)),
        max(0.0, min(1.0, p_draw_final)),
        max(0.0, min(1.0, p_away_final))
    )
