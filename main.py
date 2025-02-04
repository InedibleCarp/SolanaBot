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
        self.rate_limit_delay = 0.2  # 200ms delay between requests
        
    def _make_rpc_request(self, method: str, params: List[Any]) -> Dict:
        """Make RPC request with rate limiting and error handling"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": method,
                "params": params
            }
            
            time.sleep(self.rate_limit_delay)  # Rate limiting
            response = self.session.post(self.rpc_url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            if "error" in data:
                raise Exception(f"RPC Error: {data['error']}")
                
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during {method}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error during {method}: {str(e)}")
            raise

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

    def get_token_holders(self, token_address: str, limit: int = 100) -> Tuple[int, List[Dict]]:
        """Get token holder information with pagination support"""
        try:
            response = self._make_rpc_request(
                "getTokenAccountsByMint",
                [token_address, {"encoding": "jsonParsed"}]
            )
            
            accounts = response.get("result", {}).get("value", [])
            
            # Process and sort holders by balance
            holders = []
            for account in accounts:
                token_amount = account.get("account", {}).get("data", {}).get("parsed", {}).get("info", {}).get("tokenAmount", {})
                if token_amount.get("uiAmount") is not None:
                    holders.append({
                        "address": account["pubkey"],
                        "balance": token_amount["uiAmount"],
                        "delegate": account.get("account", {}).get("data", {}).get("parsed", {}).get("info", {}).get("delegate"),
                        "state": account.get("account", {}).get("data", {}).get("parsed", {}).get("info", {}).get("state")
                    })
            
            # Sort holders by balance
            holders.sort(key=lambda x: x["balance"], reverse=True)
            
            return len(holders), holders[:limit]
            
        except Exception as e:
            logger.error(f"Error getting token holders: {str(e)}")
            raise

    def get_token_activity(self, token_address: str, limit: int = 10) -> List[Dict]:
        """Get recent token activity with detailed transaction info"""
        try:
            signatures = self._make_rpc_request(
                "getSignaturesForAddress",
                [token_address, {"limit": limit}]
            )
            
            transactions = []
            for sig_info in signatures.get("result", []):
                tx_data = self._make_rpc_request(
                    "getTransaction",
                    [sig_info["signature"], {"encoding": "jsonParsed"}]
                )
                
                tx_result = tx_data.get("result", {})
                timestamp = datetime.fromtimestamp(tx_result.get("blockTime", 0))
                
                transactions.append({
                    "signature": sig_info["signature"],
                    "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "success" if not tx_result.get("meta", {}).get("err") else "failed",
                    "slot": sig_info["slot"],
                    "fee": tx_result.get("meta", {}).get("fee", 0),
                })
                
            return transactions
            
        except Exception as e:
            logger.error(f"Error getting token activity: {str(e)}")
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
            
            # Get and display holder information
            print("\nFetching holder information...")
            total_holders, top_holders = self.get_token_holders(token_address, limit=5)
            print(f"Total Holders: {total_holders:,}")
            print("\nTop 5 Holders:")
            for idx, holder in enumerate(top_holders, 1):
                print(f"{idx}. Address: {holder['address']}")
                print(f"   Balance: {holder['balance']:,.2f}")
                if holder['delegate']:
                    print(f"   Delegated To: {holder['delegate']}")
                    
            # Get and display recent activity
            print("\nFetching recent activity...")
            transactions = self.get_token_activity(token_address, limit=5)
            print("\nRecent Transactions:")
            for tx in transactions:
                print(f"Signature: {tx['signature']}")
                print(f"Time: {tx['timestamp']}")
                print(f"Status: {tx['status']}")
                print(f"Fee: {tx['fee']} lamports")
                print("---")
                
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
    