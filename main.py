import requests
import time
from datetime import datetime
import json
from typing import Dict, Tuple, List, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SolanaTokenBot:
    def __init__(self, rpc_url: str = "https://api.mainnet-beta.solana.com"):
        self.rpc_url = rpc_url
        self.session = requests.Session()
        # Add proper headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0',
            'Accept': '*/*'
        })
        self.rate_limit_delay = 0.5  # 500ms delay between requests
        
        # Backup RPC endpoints - public nodes that don't require API keys
        self.backup_rpcs = [
            "https://api.mainnet-beta.solana.com",
            "https://rpc.ankr.com/solana_free",
            "https://solana.public-rpc.com",
            "https://free.rpcpool.com",
            "https://api.solanium.io"
        ]
        
        # Increase timeout to handle slower public nodes
        self.session.timeout = 30

    def _make_rpc_request(self, method: str, params: List[Any]) -> Dict:
        """Make RPC request with rate limiting, error handling, and fallback endpoints"""
        last_error = None
        
        # Try main RPC endpoint first, then fallbacks
        endpoints = [self.rpc_url] + self.backup_rpcs
        
        for endpoint in endpoints:
            try:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": method,
                    "params": params
                }
                
                time.sleep(self.rate_limit_delay)  # Rate limiting
                response = self.session.post(endpoint, json=payload)
                response.raise_for_status()
                
                data = response.json()
                if "error" in data:
                    raise Exception(f"RPC Error: {data['error']}")
                    
                # If successful, update the main RPC URL to this working endpoint
                self.rpc_url = endpoint
                return data
                
            except Exception as e:
                last_error = e
                logger.warning(f"RPC request failed for endpoint {endpoint}: {str(e)}")
                continue
                
        # If we get here, all endpoints failed
        logger.error(f"All RPC endpoints failed. Last error: {str(last_error)}")
        raise Exception(f"All RPC endpoints failed: {str(last_error)}")

    def get_token_metadata(self, token_address: str) -> Dict:
        """Get comprehensive token metadata"""
        try:
            # Get token supply
            supply_data = self._make_rpc_request("getTokenSupply", [token_address])
            supply_info = supply_data.get("result", {}).get("value", {})
            
            # Get mint info
            mint_data = self._make_rpc_request("getAccountInfo", [
                token_address,
                {"encoding": "jsonParsed"}
            ])
            mint_info = mint_data.get("result", {}).get("value", {})
            
            decimals = int(supply_info.get("decimals", 0))
            total_supply = int(supply_info.get("amount", 0)) / (10 ** decimals)
            
            return {
                "token_address": token_address,
                "total_supply": total_supply,
                "decimals": decimals,
                "mint_authority": mint_info.get("data", {}).get("parsed", {}).get("info", {}).get("mintAuthority"),
                "freeze_authority": mint_info.get("data", {}).get("parsed", {}).get("info", {}).get("freezeAuthority"),
                "is_initialized": mint_info.get("data", {}).get("parsed", {}).get("info", {}).get("isInitialized", False)
            }
        except Exception as e:
            logger.error(f"Error getting token metadata: {str(e)}")
            raise

    def analyze_token(self, token_address: str) -> None:
        """Main analysis function"""
        try:
            print("\n=== Solana Token Analysis ===\n")
            
            # Get and display token metadata
            print("Fetching token metadata...")
            metadata = self.get_token_metadata(token_address)
            print(f"Token Address: {metadata['token_address']}")
            print(f"Total Supply: {metadata['total_supply']:,.2f}")
            print(f"Decimals: {metadata['decimals']}")
            print(f"Mint Authority: {metadata['mint_authority']}")
            print(f"Freeze Authority: {metadata['freeze_authority']}")
            print(f"Initialized: {metadata['is_initialized']}")
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            print(f"\nError during analysis: {str(e)}")

def main():
    bot = SolanaTokenBot()
    while True:
        try:
            token_address = input("\nEnter Solana token address (or 'quit' to exit): ").strip()
            if token_address.lower() == 'quit':
                break
                
            bot.analyze_token(token_address)
            
        except KeyboardInterrupt:
            print("\nBot stopped by user.")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            
        print("\nAnalysis complete!")

if __name__ == "__main__":
    main()
    