# Sports Betting Prediction Backend

FastAPI backend for hybrid sports betting prediction system combining statistical and fuzzy logic models.

## Setup

### Local Development

1. **Install Python 3.11+**

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access API documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Docker Deployment

```bash
docker build -t betting-prediction-api .
docker run -p 8000:8000 betting-prediction-api
```

## API Endpoints

### POST /predict
Generate prediction for a single match.

**Request:**
```json
{
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
```

**Response:**
```json
{
  "p_stat": 0.58,
  "p_fuzzy": 0.55,
  "p_hybrid": 0.565,
  "kelly_fraction": 0.08,
  "recommended_stake": 80.0
}
```

### POST /upload-data
Upload CSV file for backtesting.

**Expected CSV format:**
```csv
home_goals_avg,away_goals_avg,home_win_rate,away_win_rate,odds_home,odds_draw,odds_away,outcome
1.5,1.2,0.55,0.45,2.0,3.5,3.8,1
...
```

### POST /backtest
Run backtest on uploaded data.

### GET /experiments
Retrieve all saved experiments.

### POST /save-experiment
Save experiment results.

## Implementing Your Mathematics

The backend provides placeholder implementations. Insert your mathematical models in these files:

### 1. Fuzzy Logic Engine (`app/core/fuzzy_engine.py`)
Implement your Sugeno-type fuzzy inference system:
- Define membership functions for inputs (goals, odds)
- Create fuzzy rule base
- Implement Sugeno inference
- Return crisp probability output

### 2. Statistical Engine (`app/core/stat_engine.py`)
Implement your statistical probability model:
- Poisson distribution for goals
- Elo ratings
- Dixon-Coles model
- Or your custom statistical approach

### 3. Hybrid Engine (`app/core/hybrid_engine.py`)
Define how to combine statistical and fuzzy probabilities:
- Weighted average
- Adaptive weighting
- Ensemble methods

### 4. Kelly Criterion (`app/core/kelly.py`)
Customize Kelly calculation if needed:
- Fractional Kelly
- Risk-adjusted sizing
- Constraints and limits

### 5. Backtester (`app/core/backtester.py`)
Implement backtesting logic:
- Parse CSV data
- Apply hybrid model to historical matches
- Calculate Kelly stakes
- Track equity curve
- Compute performance metrics (ROI, Sharpe ratio, etc.)

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application and endpoints
│   ├── schemas.py           # Pydantic models for requests/responses
│   └── core/                # Core prediction engines
│       ├── __init__.py
│       ├── fuzzy_engine.py  # Fuzzy logic implementation
│       ├── stat_engine.py   # Statistical model
│       ├── hybrid_engine.py # Hybrid combination
│       ├── kelly.py         # Kelly criterion
│       └── backtester.py    # Backtesting engine
├── data/                    # Uploaded datasets (created at runtime)
├── requirements.txt
├── Dockerfile
├── .env
└── README.md
```

## Development Tips

1. **Test your models independently** before integrating into the API
2. **Use the `/docs` endpoint** to test API calls interactively
3. **Start with simple models** and iterate
4. **Validate input data** before processing
5. **Add logging** for debugging
6. **Consider edge cases** (zero probabilities, extreme odds, etc.)


## License

This is a research project for academic purposes.
