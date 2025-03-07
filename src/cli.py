from src.token_analyzer import TokenAnalyzer
from src.rpc_client import SolanaRPCClient

def run_cli():
    rpc_client = SolanaRPCClient()
    analyzer = TokenAnalyzer(rpc_client)
    
    while True:
        token_address = input("\nEnter Solana token address (or 'quit' to exit): ").strip()
        if token_address.lower() == "quit":
            break
        
        try:
            print("\n=== Solana Token Analysis ===\n")
            metadata = analyzer.get_token_metadata(token_address)
            risks = analyzer.analyze_risk(metadata)
            
            print(f"Token Address: {metadata['token_address']}")
            print(f"Total Supply: {metadata['total_supply']:,.2f}")
            print(f"Decimals: {metadata['decimals']}")
            print(f"Mint Authority: {metadata['mint_authority']}")
            print(f"Freeze Authority: {metadata['freeze_authority']}")
            print(f"Initialized: {metadata['is_initialized']}")
            print("\nRisk Assessment:")
            for key, value in risks.items():
                print(f"- {key}: {value}")
        except Exception as e:
            print(f"\nError: {str(e)}")