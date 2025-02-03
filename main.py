import requests
import pandas as pd
import time
import matplotlib.pyplot as plt

# Solana RPC Endpoint (You can use a provider like QuickNode, Alchemy, or use public RPCs)
SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"

# Function to get latest block height
def get_latest_block_height():
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSlot"
    }
    response = requests.post(SOLANA_RPC_URL, json=payload).json()
    return response.get("result", None)

# Function to get transaction count
def get_transaction_count():
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransactionCount"
    }
    response = requests.post(SOLANA_RPC_URL, json=payload).json()
    return response.get("result", None)

# Function to get active accounts (example: latest block leader)
def get_block_leader():
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getLeaderSchedule"
    }
    response = requests.post(SOLANA_RPC_URL, json=payload).json()
    return response.get("result", {}).get(str(get_latest_block_height()), ["Unknown"])[0]

# Collecting data over time
def collect_data(duration=60, interval=5):
    data = []
    start_time = time.time()

    while time.time() - start_time < duration:
        block_height = get_latest_block_height()
        tx_count = get_transaction_count()
        block_leader = get_block_leader()

        data.append({"Timestamp": time.time(), "BlockHeight": block_height, "TxCount": tx_count, "BlockLeader": block_leader})
        print(f"BlockHeight: {block_height}, TxCount: {tx_count}, BlockLeader: {block_leader}")

        time.sleep(interval)  # Pause for interval seconds

    return pd.DataFrame(data)

# Running the data collection
df = collect_data(duration=60, interval=10)

# Plot transaction count over time
plt.figure(figsize=(10, 5))
plt.plot(df["Timestamp"], df["TxCount"], marker="o", linestyle="-")
plt.xlabel("Timestamp")
plt.ylabel("Transaction Count")
plt.title("Solana Transaction Count Over Time")
plt.xticks(rotation=45)
plt.grid()
plt.show()
