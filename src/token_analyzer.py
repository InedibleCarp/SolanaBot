import logging
from typing import Dict
from src.rpc_client import SolanaRPCClient

logger = logging.getLogger(__name__)

class TokenAnalyzer:
    def __init__(self, rpc_client: SolanaRPCClient):
        self.rpc_client = rpc_client

    def get_token_metadata(self, token_address: str) -> Dict:
        """Fetch and parse token metadata from Solana blockchain."""
        try:
            supply_data = self.rpc_client.get_token_supply(token_address)
            mint_data = self.rpc_client.get_account_info(token_address)

            supply_info = supply_data.get("result", {}).get("value", {})
            mint_info = mint_data.get("result", {}).get("value", {}).get("data", {}).get("parsed", {}).get("info", {})

            decimals = int(supply_info.get("decimals", 0))
            total_supply = int(supply_info.get("amount", 0)) / (10 ** decimals)

            return {
                "token_address": token_address,
                "total_supply": total_supply,
                "decimals": decimals,
                "mint_authority": mint_info.get("mintAuthority"),
                "freeze_authority": mint_info.get("freezeAuthority"),
                "is_initialized": mint_info.get("isInitialized", False),
            }
        except Exception as e:
            logger.error(f"Error fetching metadata for {token_address}: {str(e)}")
            raise

    def analyze_risk(self, metadata: Dict) -> Dict:
        """Assess token risk based on authority settings."""
        risks = {}
        if metadata["mint_authority"]:
            risks["centralized_mint"] = "Mint authority exists, additional tokens can be created."
        if metadata["freeze_authority"]:
            risks["freeze_risk"] = "Freeze authority exists, tokens can be frozen."
        return risks