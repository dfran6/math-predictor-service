from pydantic import BaseModel, Field
from typing import List

class PredictionRequest(BaseModel):
    home_goals_avg: float = Field(..., description="Average goals scored by home team")
    away_goals_avg: float = Field(..., description="Average goals scored by away team")
    home_win_rate: float = Field(..., ge=0, le=1, description="Home team win rate")
    away_win_rate: float = Field(..., ge=0, le=1, description="Away team win rate")
    odds_home: float = Field(..., gt=1, description="Betting odds for home win")
    odds_draw: float = Field(..., gt=1, description="Betting odds for draw")
    odds_away: float = Field(..., gt=1, description="Betting odds for away win")
    bankroll: float = Field(..., gt=0, description="Total bankroll available")
    kelly_fraction: float = Field(default=0.5, ge=0, le=1, description="Kelly fraction multiplier")

    class Config:
        json_schema_extra= {
            "example": {
                "home_goals_avg": 1.5,
                "away_goals_avg": 1.2,
                "home_win_rate": 0.55,
                "away_win_rate": 0.45,
                "odds_home": 2.0,
                "odds_draw": 3.5,
                "odds_away": 3.8,
                "bankroll": 1000,
                "kelly_fraction": 0.5
            }
        }

class PredictionResponse(BaseModel):
    # Statistical model probabilities
    p_stat_home: float = Field(..., ge=0, le=1, description="Statistical probability - home win")
    p_stat_draw: float = Field(..., ge=0, le=1, description="Statistical probability - draw")
    p_stat_away: float = Field(..., ge=0, le=1, description="Statistical probability - away win")
    
    # Fuzzy logic model probabilities
    p_fuzzy_home: float = Field(..., ge=0, le=1, description="Fuzzy logic probability - home win")
    p_fuzzy_draw: float = Field(..., ge=0, le=1, description="Fuzzy logic probability - draw")
    p_fuzzy_away: float = Field(..., ge=0, le=1, description="Fuzzy logic probability - away win")
    
    # Hybrid combined probabilities
    p_hybrid_home: float = Field(..., ge=0, le=1, description="Hybrid combined probability - home win")
    p_hybrid_draw: float = Field(..., ge=0, le=1, description="Hybrid combined probability - draw")
    p_hybrid_away: float = Field(..., ge=0, le=1, description="Hybrid combined probability - away win")
    
    # Recommendation
    kelly_fraction: float = Field(..., description="Optimal Kelly fraction")
    recommended_stake: float = Field(..., description="Recommended stake amount")
    recommended_outcome: str = Field(..., description="Recommended bet: 'home', 'draw', or 'away'")

class BacktestResponse(BaseModel):
    roi: float = Field(..., description="Return on investment percentage")
    total_bets: int = Field(..., description="Total number of bets placed")
    winning_bets: int = Field(..., description="Number of winning bets")
    losing_bets: int = Field(..., description="Number of losing bets")
    equity_curve: List[float] = Field(..., description="Bankroll progression over time")
    final_bankroll: float = Field(..., description="Final bankroll amount")

class ExperimentCreate(BaseModel):
    model_name: str = Field(..., description="Name/version of the model")
    roi: float = Field(..., description="Return on investment achieved")
    accuracy: float = Field(..., ge=0, le=1, description="Prediction accuracy")
    kelly_fraction: float = Field(..., ge=0, le=1, description="Kelly fraction used")
    notes: str = Field(default="", description="Additional notes about the experiment")

class Experiment(ExperimentCreate):
    id: str = Field(..., description="Unique experiment identifier")
    date: str = Field(..., description="Date of experiment")
