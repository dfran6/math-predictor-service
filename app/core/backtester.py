"""
Backtesting Engine

Runs historical simulations on uploaded datasets.

TODO: INSERT YOUR BACKTESTING LOGIC HERE
- Load and parse CSV data
- Apply hybrid model to each match
- Calculate Kelly stakes
- Track bankroll evolution
- Compute performance metrics
"""

import csv
from typing import Dict, List
from app.core import fuzzy_engine, stat_engine, hybrid_engine, kelly

async def run_backtest(data_path: str, initial_bankroll: float = 7000.0) -> Dict:
    """
    Run backtest on historical data
    
    Args:
        data_path: Path to CSV file with match data
        initial_bankroll: Starting bankroll amount
    
    Returns:
        Dictionary with backtest results
    
    Expected CSV format:
        home_goals_avg, away_goals_avg, home_win_rate, away_win_rate,
        odds_home, odds_draw, odds_away, outcome
    
    Backtesting process:
    1. For each match in dataset:
       a. Generate prediction using hybrid model
       b. Calculate Kelly stake
       c. Place bet (if stake > 0)
       d. Update bankroll based on outcome
       e. Record result
    
    2. Calculate metrics:
       - ROI = (final - initial) / initial * 100
       - Win rate = wins / total_bets
       - Equity curve = bankroll over time
    """
    
    bankroll = initial_bankroll
    equity_curve = [bankroll]
    total_bets = 0
    winning_bets = 0
    
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    # Parse match data from CSV
                    home_goals_avg = float(row.get('home_goals_avg'))
                    # print(home_goals_avg)
                    away_goals_avg = float(row.get('away_goals_avg'))
                    home_win_rate = float(row.get('home_win_rate'))
                    away_win_rate = float(row.get('away_win_rate'))
                    odds_home = float(row.get('odds_home'))
                    odds_draw = float(row.get('odds_draw'))
                    odds_away = float(row.get('odds_away'))
                    outcome = int(row.get('outcome'))  # 1=home win, 0=else
                    
                    # Validate inputs
                    
                    # print(odds_home)
                    # print(odds_draw)
                    # print(odds_away)
                    if odds_home >= 1.0 or odds_draw >= 1.0 or odds_away >= 1.0:
                        continue
                        
                    if not (0 <= home_win_rate <= 1) or not (0 <= away_win_rate <= 1): 
                        continue
                    
                    # Generate predictions using hybrid model
                    p_stat = stat_engine.calculate_probability(
                        home_goals_avg, away_goals_avg, home_win_rate, away_win_rate
                    )
                    p_fuzzy = fuzzy_engine.calculate_probability(
                        home_goals_avg, away_goals_avg, odds_home, odds_draw, odds_away
                    )
                    p_hybrid = hybrid_engine.combine_probabilities(p_stat, p_fuzzy)
                    
                    # Only bet if probability > implied probability with edge
                    implied_prob = 1.0 / odds_home
                    min_edge = 0.02  # Need at least 2% edge
                    
                    if p_hybrid <= (implied_prob + min_edge):
                        continue
                    
                    # Calculate Kelly stake
                    kelly_frac, stake = kelly.calculate_stake(
                        p_hybrid, odds_home, bankroll, kelly_fraction=0.25
                    )
                    
                    if stake <= 0:
                        continue
                    
                    # Record bet
                    total_bets += 1
                    
                    print(total_bets)
                    # Determine outcome
                    if outcome == 1:  # Home team won
                        winning_bets += 1
                        profit = stake * (odds_home - 1)
                        bankroll += profit
                    else:  # Loss
                        bankroll -= stake
                    
                    # Track equity curve
                    equity_curve.append(bankroll)
                
                except (ValueError, KeyError):
                    # Skip malformed rows
                    continue
    
        # Calculate performance metrics
        losing_bets = total_bets - winning_bets
        roi = ((bankroll - initial_bankroll) / initial_bankroll) * 100 if initial_bankroll > 0 else 0
        
        return {
            "roi": round(roi, 2),
            "total_bets": total_bets,
            "winning_bets": winning_bets,
            "losing_bets": losing_bets,
            "equity_curve": [round(v, 2) for v in equity_curve],
            "final_bankroll": round(bankroll, 2)
        }
    except FileNotFoundError:
            print('file not found')
    
