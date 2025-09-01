# Hermes AI Market Analysis Backend

## Setup Instructions

1. Clone the repo and enter the backend folder:
   ```bash
   cd backend
   ```
2. Create a `.env` file with your API keys:
   ```
   ALPHA_VANTAGE_API_KEY=your_key
   BINANCE_API_KEY=your_key
   POSTGRES_URL=postgresql://user:pass@host:port/dbname
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

## Structure
- `main.py`: FastAPI app
- `config.py`: Loads .env config
- `scripts/`: Data fetch, training, sentiment analysis
- `CHANGES`: Log of all changes

## Docker
Docker setup will be added in the next step.
