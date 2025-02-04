import requests
import pandas as pd
import time
import matplotlib.pyplot as plt

# Solana RPC Endpoint
SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"

# Wallet to track (Replace with any Solana address)
WATCHED_WALLET = "YourWalletAddressHere"

# Function to get latest block height
def get_latest_block_height():
    payload = {"jsonrpc": "2.0", "id": 1, "method": "getSlot"}
    response = requests.post(SOLANA_RPC_URL, json=payload).json()
    return response.get("result", None)

# Function to get transaction count
def get_transaction_count():
    payload = {"jsonrpc": "2.0", "id": 1, "method": "getTransactionCount"}
    response = requests.post(SOLANA_RPC_URL, json=payload).json()
    return response.get("result", None)

# Function to get transactions for a specific wallet
def get_wallet_transactions(wallet_address, limit=10):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [wallet_address, {"limit": limit}]
    }
    response = requests.post(SOLANA_RPC_URL, json=payload).json()
    return response.get("result", [])

# Function to get details of a specific transaction
def get_transaction_details(signature):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [signature, {"encoding": "json"}]
    }
    response = requests.post(SOLANA_RPC_URL, json=payload).json()
    return response.get("result", {})

# Collect data over time
def collect_data(duration=60, interval=10):
    data = []
    start_time = time.time()

    while time.time() - start_time < duration:
        block_height = get_latest_block_height()
        tx_count = get_transaction_count()
        transactions = get_wallet_transactions(WATCHED_WALLET, limit=5)

        # Extracting transaction signatures
        tx_signatures = [tx["signature"] for tx in transactions]

        # Fetching details of each transaction
        tx_details = [get_transaction_details(sig) for sig in tx_signatures]

        # Extract relevant transaction info
        parsed_tx = []
        for tx in tx_details:
            if tx:
                block_time = tx.get("blockTime", None)
                fee = tx.get("meta", {}).get("fee", None)
                signatures = tx.get("transaction", {}).get("signatures", [])
                accounts = tx.get("transaction", {}).get("message", {}).get("accountKeys", [])
                
                parsed_tx.append({"BlockTime": block_time, "Fee": fee, "Signatures": signatures, "Accounts": accounts})

        # Log transactions and add to data
        data.append({"Timestamp": time.time(), "BlockHeight": block_height, "TxCount": tx_count, "WalletTx": parsed_tx})
        print(f"BlockHeight: {block_height}, TxCount: {tx_count}, WalletTxCount: {len(parsed_tx)}")

        time.sleep(interval)  # Pause for interval seconds

    return pd.DataFrame(data)

# Run data collection
df = collect_data(duration=60, interval=10)

# Extract transaction counts for visualization
df["WalletTxCount"] = df["WalletTx"].apply(len)

# Plot wallet transaction count over time
plt.figure(figsize=(10, 5))
plt.plot(df["Timestamp"], df["WalletTxCount"], marker="o", linestyle="-", color="blue")
plt.xlabel("Timestamp")
plt.ylabel("Wallet Transaction Count")
plt.title(f"Transactions for Wallet {WATCHED_WALLET} Over Time")
plt.xticks(rotation=45)
plt.grid()
plt.show()
