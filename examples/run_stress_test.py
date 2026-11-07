from src.data_loader import FinancialDataLoader
from src.valuation import StressedValuationEngine


def run_pipeline(ticker_symbol: str):
    # 1. Fetch live market cap and pricing
    loader = FinancialDataLoader(ticker_symbol)
    market_data = loader.fetch_market_data()
    bs_data = loader.fetch_balance_sheet_summary()

    print(f"Loaded live data for {market_data['company_name']} ({market_data['ticker']})")
    print(f"Live Market Cap: ${market_data['market_cap']:,.2f}")
    
    # 2. Set credit parameters (pulled from 10-K notes or custom stress scenario)
    tce = bs_data["stockholders_equity"] or 4_500_000_000.0  # Fallback if unparsed
    total_portfolio = 12_000_000_000.0                       # Unpaid Principal Balance (UPB)
    current_acl = 300_000_000.0                              # Allowance for Credit Losses
    
    # 3. Initialize & run Valuation Engine
    engine = StressedValuationEngine(
        ticker=ticker_symbol,
        tangible_common_equity=tce,
        total_loan_portfolio=total_portfolio,
        current_acl=current_acl,
        cost_of_equity=0.11
    )

    results = engine.calculate_intrinsic_value(
        stressed_default_rate=0.08,
        recovery_rate=0.25,
        stressed_earnings=250_000_000.0,
        projection_years=3
    )

    alpha = engine.calculate_alpha(market_data['market_cap'], results['intrinsic_equity_value'])

    print("\n--- VALUATION SUMMARY ---")
    print(f"Stressed Intrinsic Value: ${results['intrinsic_equity_value']:,.2f}")
    print(f"Mispricing Spread (Alpha): ${alpha:,.2f}")


if __name__ == "__main__":
    run_pipeline("SLM")