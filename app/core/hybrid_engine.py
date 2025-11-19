"""
Hybrid Probability Engine

Combines statistical and fuzzy logic probabilities.

TODO: INSERT YOUR HYBRID COMBINATION METHOD HERE
- Weighted average
- Adaptive weighting based on confidence
- Ensemble methods
- Or your custom approach
"""

def combine_probabilities(
    p_stat: tuple[float, float, float],
    p_fuzzy: tuple[float, float, float],
    stat_confidence: float = 0.5,
    fuzzy_confidence: float = 0.5
) -> tuple[float, float, float]:
    """
    Combine statistical and fuzzy probabilities for all outcomes
    
    Args:
        p_stat: Tuple of (p_home, p_draw, p_away) from statistical model
        p_fuzzy: Tuple of (p_home, p_draw, p_away) from fuzzy logic model
        stat_confidence: Confidence in statistical model (0-1)
        fuzzy_confidence: Confidence in fuzzy model (0-1)
    
    Returns:
        Tuple of (p_home, p_draw, p_away) combined hybrid probabilities
    """
    
    # Normalize confidences
    total_conf = stat_confidence + fuzzy_confidence
    if total_conf == 0:
        stat_confidence = fuzzy_confidence = 0.5
        total_conf = 1.0
    
    w_stat = stat_confidence / total_conf
    w_fuzzy = fuzzy_confidence / total_conf
    
    # Combine each outcome
    p_home = w_stat * p_stat[0] + w_fuzzy * p_fuzzy[0]
    p_draw = w_stat * p_stat[1] + w_fuzzy * p_fuzzy[1]
    p_away = w_stat * p_stat[2] + w_fuzzy * p_fuzzy[2]
    
    # Normalize to sum to 1.0
    total = p_home + p_draw + p_away
    if total > 0:
        p_home /= total
        p_draw /= total
        p_away /= total
    else:
        p_home = p_draw = p_away = 1.0 / 3.0
    
    return (
        max(0.0, min(1.0, p_home)),
        max(0.0, min(1.0, p_draw)),
        max(0.0, min(1.0, p_away))
    )
    
    w_stat = stat_confidence / total_conf
    w_fuzzy = fuzzy_confidence / total_conf
    
    # Adaptive weighted average: models with higher confidence get higher weight
    p_hybrid = w_stat * p_stat + w_fuzzy * p_fuzzy
    
    return max(0.0, min(1.0, p_hybrid))
