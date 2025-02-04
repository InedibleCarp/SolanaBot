import requests
import time

# Solana RPC Endpoint
SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"

# Function to get token metadata
def get_token_metadata(token_address):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenSupply",
        "params": [token_address]
    }
    response = requests.post(SOLANA_RPC_URL, json=payload).json()
    supply_info = response.get("result", {})
    
    return {
        "TokenAddress": token_address,
        "Supply": int(supply_info.get("value", {}).get("amount", 0)) / (10 ** int(supply_info.get("value", {}).get("decimals", 0))),
        "Decimals": supply_info.get("value", {}).get("decimals", 0)
    }

# Function to get token accounts (holders)
def get_token_holders(token_address):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenAccountsByMint",
        "params": [
            token_address,
            {"encoding": "jsonParsed"}
        ]
    }
    response = requests.post(SOLANA_RPC_URL, json=payload).json()
    accounts = response.get("result", {}).get("value", [])
    return len(accounts), accounts[:5]  # Return total holders and first 5 for demonstration

# Function to analyze token activity
def get_recent_transactions(token_address):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [token_address, {"limit": 5}]
    }
    response = requests.post(SOLANA_RPC_URL, json=payload).json()
    transactions = response.get("result", [])
    return transactions

# Main function
def token_insight_bot():
    print("Welcome to the Solana Token Insight Bot!")
    token_address = input("Please enter the Solana token address: ")

    print("\nFetching token metadata...")
    metadata = get_token_metadata(token_address)
    print(f"Token Address: {metadata['TokenAddress']}")
    print(f"Total Supply: {metadata['Supply']}")
    print(f"Decimals: {metadata['Decimals']}")

    print("\nFetching token holders...")
    total_holders, top_holders = get_token_holders(token_address)
    print(f"Total Token Holders: {total_holders}")
    print("Sample Holders:")
    for holder in top_holders:
        print(f"- {holder['pubkey']} with balance: {holder['account']['data']['parsed']['info']['tokenAmount']['uiAmount']}")

    print("\nFetching recent transactions...")
    transactions = get_recent_transactions(token_address)
    print(f"Recent Transactions (Last {len(transactions)}):")
    for tx in transactions:
        print(f"- Signature: {tx['signature']} | Slot: {tx['slot']} | Confirmed: {tx['confirmationStatus']}")

    print("\nAnalysis Complete!")
    print("You can use this bot again to analyze another token.")

# Run the bot
if __name__ == "__main__":
    token_insight_bot()
