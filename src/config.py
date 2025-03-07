from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    RPC_URL = os.getenv("RPC_URL", "https://api.mainnet-beta.solana.com")
    BACKUP_RPCS = [
        "https://api.mainnet-beta.solana.com",
        "https://rpc.ankr.com/solana_free",
        "https://solana.public-rpc.com",
    ]
    RATE_LIMIT_DELAY = float(os.getenv("RATE_LIMIT_DELAY", 0.5))
    TIMEOUT = int(os.getenv("TIMEOUT", 30))