import logging
from src.cli import run_cli

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("solana_analyzer.log"), logging.StreamHandler()],
)

if __name__ == "__main__":
    run_cli()