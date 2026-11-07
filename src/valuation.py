import numpy as np
import pandas as pd


class StressedValuationEngine:
    def __init__(
        self,
        ticker: str,
        tangible_common_equity: float,
        total_loan_portfolio: float,
        current_acl: float,
        cost_of_equity: float = 0.11,
    ):
        self.ticker = ticker
        self.tce = tangible_common_equity
        self.portfolio = total_loan_portfolio
        self.current_acl = current_acl
        self.re = cost_of_equity

    def compute_stressed_book_value(
        self, stressed_default_rate: float, recovery_rate: float
    ) -> float:
        "Calculates tangible book value adjusted for unreserved credit losses under stress."
        expected_losses = (self.portfolio * stressed_default_rate) * (1 - recovery_rate)
        unreserved_losses = max(0.0, expected_losses - self.current_acl)
        bv_adj = self.tce - unreserved_losses
        return bv_adj

    def calculate_intrinsic_value(
        self,
        stressed_default_rate: float,
        recovery_rate: float,
        stressed_earnings: float,
        projection_years: int = 3,
    ) -> dict:
        "Computes the intrinsic equity value using a Residual Income Model (RIM)."
        bv_adj = self.compute_stressed_book_value(
            stressed_default_rate, recovery_rate
        )

        residual_income_pv = 0.0
        bv_t = bv_adj
        annual_book_values = [bv_t]

        for t in range(1, projection_years + 1):
            # Residual income = Stressed Earnings - (Cost of Equity * Beginning Book Value)
            residual_income = stressed_earnings - (self.re * bv_t)
            residual_income_pv += residual_income / ((1 + self.re) ** t)
            
            # Simple clean assumption: earnings retained add to book value
            bv_t += stressed_earnings
            annual_book_values.append(bv_t)

        intrinsic_value = bv_adj + residual_income_pv

        return {
            "ticker": self.ticker,
            "adjusted_book_value": bv_adj,
            "residual_income_pv": residual_income_pv,
            "intrinsic_equity_value": intrinsic_value,
            "projected_book_values": annual_book_values,
        }

    @staticmethod
    def calculate_alpha(market_cap: float, intrinsic_value: float) -> float:
        "Calculates mispricing spread (alpha) relative to market valuation."
        return market_cap - intrinsic_value