"""
Kelly Criterion Calculator

Implements Kelly criterion for optimal bet sizing.

TODO: Customize Kelly calculation if needed
- Fractional Kelly
- Constraints and limits
- Risk adjustments
"""

def calculate_stake(
    probability: float,
    odds: float,
    bankroll: float,
    kelly_fraction: float = 0.5
) -> tuple[float, float]:
    """
    Calculate optimal bet size using Kelly criterion
    
    Args:
        probability: Estimated win probability
        odds: Decimal odds offered by bookmaker
        bankroll: Current bankroll amount
        kelly_fraction: Fraction of Kelly to use (default 0.5 for half-Kelly)
    
    Returns:
        Tuple of (kelly_fraction_value, recommended_stake_amount)
    
    Kelly formula:
        f = (bp - q) / b
        where:
        - f = fraction of bankroll to wager
        - b = odds - 1 (net odds received)
        - p = probability of winning
        - q = 1 - p (probability of losing)
    
    Fractional Kelly:
        - Full Kelly can be aggressive
        - Half-Kelly (0.5) or quarter-Kelly (0.25) are conservative
        - Reduces variance while maintaining most growth rate
    """
    
    if probability <= 0 or probability >= 1:
        return 0.0, 0.0
    
    if odds <= 1:
        return 0.0, 0.0
    
    # Kelly formula
    b = odds - 1  # Net odds
    q = 1 - probability  # Loss probability
    
    # Full Kelly fraction
    full_kelly = (probability * b - q) / b
    
    # Apply Kelly fraction multiplier (safety factor)
    kelly = max(0, full_kelly * kelly_fraction)
    
    # Cap at 5% of bankroll per bet (risk management)
    kelly_capped = min(kelly, 0.05)
    
    # Calculate stake
    stake = bankroll * kelly_capped
    
    return round(kelly_capped, 4), round(stake, 2)
    b = odds - 1  # Net odds
    p = probability
    q = 1 - p
    
    # Full Kelly fraction
    f_kelly = (b * p - q) / b
    
    # Apply fractional Kelly multiplier
    f_adjusted = f_kelly * kelly_fraction
    
    # Only bet if Kelly is positive (edge exists)
    if f_adjusted <= 0:
        return 0.0, 0.0
    
    # Cap at reasonable maximum (e.g., 25% of bankroll)
    f_adjusted = min(f_adjusted, 0.25)
    
    # Calculate stake amount
    stake = bankroll * f_adjusted
    
    return f_adjusted, stake
