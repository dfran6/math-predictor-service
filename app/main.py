from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import PredictionRequest, PredictionResponse, BacktestResponse, ExperimentCreate, Experiment
from app.core import fuzzy_engine, stat_engine, hybrid_engine, kelly, backtester
import uuid
from datetime import datetime
from typing import List
import os
import csv

app = FastAPI(
    title="Sports Betting Prediction API",
    description="Hybrid statistical and fuzzy logic prediction system for sports betting",
    version="1.0.0"
)

origins = [
  "https://fuzzymathpredictor.vercel.app/",
  "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


uploaded_data = None
experiments_db: List[Experiment] = []

@app.get("/")
async def read_root():
    return {
        "message": "Sports Betting Prediction API",
        "version": "1.0.0",
        "endpoints": ["/predict", "/upload-data", "/backtest", "/experiments", "/save-experiment"]
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Generate predictions using hybrid model (statistical + fuzzy logic)
    for all three outcomes: home win, draw, and away win
    """
    try:
        # Validate inputs
        if request.home_goals_avg < 0 or request.away_goals_avg < 0:
            raise ValueError("Goals average cannot be negative")
        if not (0 < request.home_win_rate < 1):
            raise ValueError("Home win rate must be between 0 and 1")
        if not (0 < request.away_win_rate < 1):
            raise ValueError("Away win rate must be between 0 and 1")
        
        # Calculate statistical probability for all outcomes
        p_stat = stat_engine.calculate_probability(
            request.home_goals_avg,
            request.away_goals_avg,
            request.home_win_rate,
            request.away_win_rate
        )
        
        # Calculate fuzzy logic probability for all outcomes
        p_fuzzy = fuzzy_engine.calculate_probability(
            request.home_goals_avg,
            request.away_goals_avg,
            request.odds_home,
            request.odds_draw,
            request.odds_away
        )
        
        # Combine using hybrid engine for all outcomes
        p_hybrid = hybrid_engine.combine_probabilities(p_stat, p_fuzzy)
        
        # Find best betting opportunity (highest edge)
        total_odds_inv = 1/request.odds_home + 1/request.odds_draw + 1/request.odds_away
        implied_home = (1/request.odds_home) / total_odds_inv
        implied_draw = (1/request.odds_draw) / total_odds_inv
        implied_away = (1/request.odds_away) / total_odds_inv
        
        # Edge = probability - implied_probability
        edges = {
            "home": p_hybrid[0] - implied_home,
            "draw": p_hybrid[1] - implied_draw,
            "away": p_hybrid[2] - implied_away
        }
        
        # Select best outcome
        best_outcome = max(edges, key=edges.get)
        
        # Get odds and probability for best outcome
        best_odds = {
            "home": request.odds_home,
            "draw": request.odds_draw,
            "away": request.odds_away
        }[best_outcome]
        
        best_probability = p_hybrid[
            0 if best_outcome == "home" else 
            1 if best_outcome == "draw" else 
            2
        ]
        
        # Calculate Kelly criterion and recommended stake for best outcome
        kelly_fraction, recommended_stake = kelly.calculate_stake(
            best_probability,
            best_odds,
            request.bankroll,
            request.kelly_fraction
        )
        
        return PredictionResponse(
            p_stat_home=round(p_stat[0], 4),
            p_stat_draw=round(p_stat[1], 4),
            p_stat_away=round(p_stat[2], 4),
            p_fuzzy_home=round(p_fuzzy[0], 4),
            p_fuzzy_draw=round(p_fuzzy[1], 4),
            p_fuzzy_away=round(p_fuzzy[2], 4),
            p_hybrid_home=round(p_hybrid[0], 4),
            p_hybrid_draw=round(p_hybrid[1], 4),
            p_hybrid_away=round(p_hybrid[2], 4),
            kelly_fraction=kelly_fraction,
            recommended_stake=recommended_stake,
            recommended_outcome=best_outcome
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/upload-data")
async def upload_data(file: UploadFile = File(...)):
    """
    Upload CSV file for backtesting
    Expected columns: home_goals_avg, away_goals_avg, home_win_rate, away_win_rate, 
                      odds_home, odds_draw, odds_away, outcome
    """
    global uploaded_data
    
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    # Check file size (max 50MB)
    max_size = 50 * 1024 * 1024
    file_size = 0
    
    try:
        # Create data directory
        upload_dir = "data"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Sanitize filename
        safe_filename = "".join(c for c in file.filename if c.isalnum() or c in ('-', '_', '.'))
        file_path = os.path.join(upload_dir, safe_filename)
        
        # Write and validate file
        content = await file.read()
        file_size = len(content)
        
        if file_size > max_size:
            raise HTTPException(status_code=413, detail=f"File too large. Max {max_size / 1024 / 1024}MB")
        
        if file_size == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Write file
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Validate CSV structure
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise HTTPException(status_code=400, detail="Invalid CSV format")
        
        uploaded_data = file_path
        
        return {
            "message": "File uploaded successfully",
            "filename": safe_filename,
            "size": file_size
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")

@app.post("/backtest", response_model=BacktestResponse)
async def run_backtest():
    """
    Run backtest on uploaded data
    
    INSERT YOUR BACKTEST LOGIC HERE:
    - Load uploaded CSV
    - Apply hybrid model to each row
    - Calculate Kelly stakes
    - Track equity curve
    - Compute performance metrics
    """
    global uploaded_data
    
    if not uploaded_data:
        raise HTTPException(status_code=400, detail="No data uploaded. Please upload a CSV file first.")
    
    try:
        # Placeholder backtest logic
        result = await backtester.run_backtest(uploaded_data)
        
        return BacktestResponse(
            roi=result["roi"],
            total_bets=result["total_bets"],
            winning_bets=result["winning_bets"],
            losing_bets=result["losing_bets"],
            equity_curve=result["equity_curve"],
            final_bankroll=result["final_bankroll"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest error: {str(e)}")

@app.get("/experiments", response_model=List[Experiment])
async def get_experiments():
    """
    Retrieve all saved experiments
    """
    return experiments_db

@app.post("/save-experiment", response_model=Experiment)
async def save_experiment(experiment: ExperimentCreate):
    """
    Save experiment results
    """
    new_experiment = Experiment(
        id=str(uuid.uuid4()),
        date=datetime.now().isoformat(),
        **experiment.dict()
    )
    experiments_db.append(new_experiment)
    return new_experiment

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
