import requests
import time
import logging
from typing import Dict, List, Any
from tenacity import retry, stop_after_attempt, wait_exponential
from src.config import Config

logger = logging.getLogger(__name__)

class SolanaRPCClient:
    def __init__(self):
        self.rpc_url = Config.RPC_URL
        self.backup_rpcs = Config.BACKUP_RPCS
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
            "Accept": "*/*",
        })
        self.session.timeout = Config.TIMEOUT

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    def _make_rpc_request(self, method: str, params: List[Any]) -> Dict:
        endpoints = [self.rpc_url] + self.backup_rpcs
        last_error = None

        for endpoint in endpoints:
            try:
                payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
                time.sleep(Config.RATE_LIMIT_DELAY)
                response = self.session.post(endpoint, json=payload)
                response.raise_for_status()
                data = response.json()
                if "error" in data:
                    raise Exception(f"RPC Error: {data['error']}")
                self.rpc_url = endpoint  # Update to working endpoint
                return data
            except Exception as e:
                last_error = e
                logger.warning(f"RPC request failed for {endpoint}: {str(e)}")
                continue
        raise Exception(f"All RPC endpoints failed: {str(last_error)}")

    def get_token_supply(self, token_address: str) -> Dict:
        return self._make_rpc_request("getTokenSupply", [token_address])

    def get_account_info(self, token_address: str) -> Dict:
        return self._make_rpc_request("getAccountInfo", [token_address, {"encoding": "jsonParsed"}])