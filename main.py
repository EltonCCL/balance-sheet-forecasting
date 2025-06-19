import json
import os
import pprint
import re

import pandas as pd
import yfinance as yf

from utils import build_recursively, sum_dict_values

yf.set_tz_cache_location(".yf_cache")


class CompanyFS:
    def __init__(self, ticker: str):
        assert isinstance(ticker, str), "Ticker must be a string"
        self.ticker_name = ticker.upper()
        self.ticker = yf.Ticker(ticker.upper())

        self.balancesheet = self.ticker.balancesheet
        self.incomestatement = self.ticker.financials
        self.cashflow = self.ticker.cashflow

    def get_bs_df(self, date: str) -> pd.Series:
        assert isinstance(date, str), "Date must be a string"
        assert date in self.balancesheet.columns, "Date not found in balancesheet"
        return self.balancesheet[date]

    def get_bs(self, date: str) -> dict:
        """
        Gets the balance sheet for a given date with predefined structure.
        """
        assert isinstance(date, str), "Date must be a string"
        assert date in self.balancesheet.columns, "Date not found in balancesheet"

        # find configurations
        folder_path = f"config/{self.ticker_name}"
        if not os.path.exists(folder_path):
            assert False, f"Folder {folder_path} does not exist. Please create it."

        # load balance sheet map
        balance_sheet_map_path = f"{folder_path}/balance_sheet_map.json"
        assert os.path.exists(balance_sheet_map_path), (
            f"Balance sheet map file {balance_sheet_map_path} does not exist. "
            "Please create it."
        )

        balance_sheet_map = {}
        # load the balance sheet map
        with open(balance_sheet_map_path, "r") as f:
            balance_sheet_map = json.load(f)

        bs_df_series = self.get_bs_df(date)
        assert isinstance(bs_df_series, pd.Series), "Balance sheet data is not a Series"

        # build the balance sheet dictionary recursively
        bs_dict = build_recursively(balance_sheet_map, bs_df_series)
        assert isinstance(bs_dict, dict), "Balance sheet data is not a dictionary"

        # validation
        assert (
            sum_dict_values(bs_dict["total_assets"]) == bs_df_series["Total Assets"]
        ), "Total assets do not match the sum of current and non-current assets."

        assert (
            sum_dict_values(bs_dict["total_liabilities"])
            == bs_df_series["Total Liabilities Net Minority Interest"]
        ), "Total liabilities do not match the sum of current and non-current liabilities."

        assert (
            sum_dict_values(bs_dict["total_equity"])
            == bs_df_series["Total Equity Gross Minority Interest"]
        ), "Total equity does not match the sum of capital stock, retained earnings, and gains/losses not affecting retained earnings."

        assert (
            sum_dict_values(bs_dict["total_assets"])
            - sum_dict_values(bs_dict["total_liabilities"])
            - sum_dict_values(bs_dict["total_equity"])
            == 0
        ), "The balance sheet equation does not hold: Total Assets = Total Liabilities + Total Equity."

        assert (
            bs_df_series["Total Assets"]
            - bs_df_series["Total Liabilities Net Minority Interest"]
            - bs_df_series["Total Equity Gross Minority Interest"]
            == 0
        ), "The real balance sheet equation does not hold: Total Assets = Total Liabilities + Total Equity."

        assert sum_dict_values(bs_dict) == (
            bs_df_series["Total Assets"]
            + bs_df_series["Total Liabilities Net Minority Interest"]
            + bs_df_series["Total Equity Gross Minority Interest"]
        ), "Total balance sheet does not match the actual sum of total assets, total liabilities, and total equity."

        return bs_dict

    def get_pnl_df(self, date: str) -> pd.Series:
        assert isinstance(date, str), "Date must be a string"
        assert date in self.incomestatement.columns, "Date not found in incomestatement"

        return self.incomestatement[date]

    def get_pnl(self, date: str) -> dict:
        """
        Gets the income statement for a given date with predefined structure.
        """
        assert isinstance(date, str), "Date must be a string"
        assert date in self.incomestatement.columns, "Date not found in incomestatement"

        # find configurations
        folder_path = f"config/{self.ticker_name}"
        if not os.path.exists(folder_path):
            assert False, f"Folder {folder_path} does not exist. Please create it."

        # load income statement map
        income_statement_map_path = f"{folder_path}/income_statement_map.json"
        assert os.path.exists(income_statement_map_path), (
            f"Income statement map file {income_statement_map_path} does not exist. "
            "Please create it."
        )

        income_statement_map = {}
        # load the income statement map
        with open(income_statement_map_path, "r") as f:
            income_statement_map = json.load(f)

        pnl_df_series = self.get_pnl_df(date)
        assert isinstance(
            pnl_df_series, pd.Series
        ), "Income statement data is not a Series"

        # build the income statement dictionary recursively
        pnl_dict = build_recursively(income_statement_map, pnl_df_series)
        assert isinstance(pnl_dict, dict), "Income statement data is not a dictionary"

        # validation
        assert (
            pnl_dict["total_revenue"] - pnl_dict["cost_of_revenue"]
            == pnl_dict["gross_profit"]
        ), "Gross profit does not match total revenue minus cost of revenue."
        assert (
            pnl_dict["gross_profit"] - pnl_dict["operating_expenses"]
            == pnl_dict["operating_income"]
        ), "Operating income does not match gross profit minus operating expenses."
        assert (
            pnl_dict["operating_income"]
            + pnl_dict["net_non_operating_interest_income_expense"]
            + pnl_dict["other_income_expense"]
            == pnl_dict["pretax_income"]
        ), "Pretax income does not match operating income minus net non-operating interest income/expense and other income/expense."
        assert (
            pnl_dict["pretax_income"] - pnl_dict["tax_provision"]
            == pnl_dict["net_income_common_stockholders"]
        ), "Net income does not match pretax income minus tax provision."

        return pnl_dict

    def get_cf_df(self, date: str) -> pd.Series:
        assert isinstance(date, str), "Date must be a string"
        assert date in self.cashflow.columns, "Date not found in cashflow"

        return self.cashflow[date]

    def get_cf(self, date: str) -> dict:
        """
        Gets the cash flow statement for a given date with predefined structure.
        """
        assert isinstance(date, str), "Date must be a string"
        assert date in self.cashflow.columns, "Date not found in cashflow"

        # find configurations
        folder_path = f"config/{self.ticker_name}"
        if not os.path.exists(folder_path):
            assert False, f"Folder {folder_path} does not exist. Please create it."

        # load cash flow map
        cash_flow_map_path = f"{folder_path}/cash_flow_map.json"
        assert os.path.exists(cash_flow_map_path), (
            f"Cash flow map file {cash_flow_map_path} does not exist. "
            "Please create it."
        )

        cash_flow_map = {}
        # load the cash flow map
        with open(cash_flow_map_path, "r") as f:
            cash_flow_map = json.load(f)

        cf_df_series = self.get_cf_df(date)
        assert isinstance(cf_df_series, pd.Series), "Cash flow data is not a Series"

        # build the cash flow dictionary recursively
        cf_dict = build_recursively(cash_flow_map, cf_df_series)
        assert isinstance(cf_dict, dict), "Cash flow data is not a dictionary"

        return cf_dict

    def forecast_balancesheet(
        self, base_year: str, num_years: int = 1, override: dict = None
    ):
        """
        Forecast balance sheet for multiple years.

        Returns:
            List of tuples: [(forecast_bs_year1, forecast_drivers_year1), ...]
            Where List[0] is the next year, List[1] is next next year, etc.
        """
        # forecast year must larger than base year
        assert isinstance(base_year, str), "Base year must be a string"
        assert isinstance(num_years, int), "Number of years must be an integer"
        assert num_years > 0, "Number of years must be greater than 0"
        assert re.match(
            r"^\d{4}-\d{2}-\d{2}$", base_year
        ), "Base year must be in YYYY-MM-DD format"

        # Get initial base year data
        base_balance_sheet: dict = self.get_bs(base_year)
        base_income_statement: dict = self.get_pnl(base_year)
        base_cash_flow: dict = self.get_cf(base_year)

        # Calculate driver attributes from base year
        driver_attributes = {
            "sales_growth_rate": 1.05,
            "operating_margin": base_income_statement["operating_income"]
            / base_income_statement["total_revenue"],
            "capex_as_percentage_of_sales": base_cash_flow["capital_expenditure"]
            / base_income_statement["total_revenue"],
            "depreciation_amortization_depletion_as_percentage_of_net_ppe": base_cash_flow[
                "depreciation_amortization_depletion"
            ]
            / base_balance_sheet["total_assets"]["non_current_assets"]["net_ppe"],
            "interest_rate_on_debt": base_income_statement[
                "net_non_operating_interest_income_expense"
            ]
            / (
                base_balance_sheet["total_liabilities"]["current_liabilities"][
                    "current_debt"
                ]
                + base_balance_sheet["total_liabilities"]["non_current_liabilities"][
                    "long_term_debt"
                ]
            ),
            "tax_rate": base_income_statement["tax_provision"]
            / base_income_statement["pretax_income"],
            "dividend_payout_ratio": base_cash_flow["cash_dividends_paid"]
            / base_income_statement["net_income_common_stockholders"],
            "minimum_cash_required": base_balance_sheet["total_assets"][
                "current_assets"
            ]["cash_and_equivalents"],
        }

        # handle overrides if provided
        if override:
            assert isinstance(override, dict), "Override must be a dictionary"
            for key, value in override.items():
                if key in driver_attributes:
                    driver_attributes[key] = value
                else:
                    print(f"Warning: {key} is not a valid driver attribute.")

        # List to store all forecasted years
        forecasted_years = []

        # Keep track of the previous year's data for iterative forecasting
        current_bs = base_balance_sheet
        previous_sales = base_income_statement["total_revenue"]

        # Forecast each year iteratively
        for year in range(num_years):
            forecast_result = self._forecast_single_year(
                current_bs, previous_sales, driver_attributes, year + 1
            )
            forecasted_years.append(forecast_result)

            # Update current_bs and previous_sales for next iteration
            current_bs = forecast_result[0]  # forecast_bs
            previous_sales = forecast_result[1]["sales"]  # forecast_drivers["sales"]

        return forecasted_years

    def _forecast_single_year(
        self,
        previous_bs: dict,
        previous_sales: float,
        driver_attributes: dict,
        year_number: int,
    ):
        """
        Helper method to forecast a single year based on previous year's balance sheet.

        Args:
            previous_bs: Previous year's balance sheet
            previous_sales: Previous year's sales
            driver_attributes: Financial drivers
            year_number: Which year we're forecasting (1, 2, 3, etc.)

        Returns:
            Tuple of (forecast_bs, forecast_drivers)
        """
        forecast_drivers = {}

        # Extract values from previous year's balance sheet
        net_ppe_prev = previous_bs["total_assets"]["non_current_assets"]["net_ppe"]
        total_debt_prev = (
            previous_bs["total_liabilities"]["current_liabilities"]["current_debt"]
            + previous_bs["total_liabilities"]["non_current_liabilities"][
                "long_term_debt"
            ]
        )
        cash_prev = previous_bs["total_assets"]["current_assets"][
            "cash_and_equivalents"
        ]
        retained_earnings_prev = previous_bs["total_equity"]["retained_earnings"]

        # --- Top-to-bottom calculation ---
        forecast_drivers["sales"] = (
            previous_sales * driver_attributes["sales_growth_rate"]
        )

        forecast_drivers["operating_income"] = (
            forecast_drivers["sales"] * driver_attributes["operating_margin"]
        )

        # Calculate Depreciation first, as it's needed for EBIT and for the Capex assumption
        forecast_drivers["depreciation"] = (
            net_ppe_prev
            * driver_attributes[
                "depreciation_amortization_depletion_as_percentage_of_net_ppe"
            ]
        )

        forecast_drivers["ebit"] = forecast_drivers["operating_income"]

        forecast_drivers["interest_expense"] = (
            total_debt_prev * driver_attributes["interest_rate_on_debt"]
        )

        forecast_drivers["pretax_income"] = (
            forecast_drivers["ebit"] - forecast_drivers["interest_expense"]
        )

        forecast_drivers["tax_provision"] = (
            forecast_drivers["pretax_income"] * driver_attributes["tax_rate"]
        )

        forecast_drivers["net_income"] = (
            forecast_drivers["pretax_income"] - forecast_drivers["tax_provision"]
        )

        # Cash Flow
        # Cash Flow from Operations (CFO)
        cfo = forecast_drivers["net_income"] + forecast_drivers["depreciation"]

        # Cash Flow from Investing (CFI)
        forecast_drivers["capex"] = forecast_drivers["depreciation"]
        cfi = -forecast_drivers["capex"]

        # Scheduled Cash Flow from Financing (CFF)
        forecast_drivers["dividends_paid"] = (
            forecast_drivers["net_income"] * driver_attributes["dividend_payout_ratio"]
        )
        scheduled_cff = -forecast_drivers["dividends_paid"]

        # --- Calculate the company's cash position BEFORE any new borrowing or investing ---
        net_cash_flow_before_new_financing = cfo + cfi + scheduled_cff
        provisional_cash_balance = cash_prev + net_cash_flow_before_new_financing

        # --- The "No-Plug" Decision Logic ---
        cash_surplus_or_deficit = (
            provisional_cash_balance - driver_attributes["minimum_cash_required"]
        )

        if cash_surplus_or_deficit < 0:
            forecast_drivers["new_debt_needed"] = -cash_surplus_or_deficit
            forecast_drivers["new_st_investment"] = 0
        else:
            forecast_drivers["new_debt_needed"] = 0
            forecast_drivers["new_st_investment"] = cash_surplus_or_deficit

        # Construct new Balance Sheet
        forecast_bs = {
            "total_assets": {"current_assets": {}, "non_current_assets": {}},
            "total_liabilities": {
                "current_liabilities": {},
                "non_current_liabilities": {},
            },
            "total_equity": {},
        }

        # Current Assets
        forecast_bs["total_assets"]["current_assets"]["cash_and_equivalents"] = (
            cash_prev
            + net_cash_flow_before_new_financing
            + forecast_drivers["new_debt_needed"]
            - forecast_drivers["new_st_investment"]
        )
        forecast_bs["total_assets"]["current_assets"]["receivables"] = previous_bs[
            "total_assets"
        ]["current_assets"]["receivables"]
        forecast_bs["total_assets"]["current_assets"]["Inventory"] = previous_bs[
            "total_assets"
        ]["current_assets"]["Inventory"]
        forecast_bs["total_assets"]["current_assets"]["hedging_assets_current"] = (
            previous_bs["total_assets"]["current_assets"]["hedging_assets_current"]
        )
        forecast_bs["total_assets"]["current_assets"]["other_current_assets"] = (
            previous_bs["total_assets"]["current_assets"]["other_current_assets"]
        )

        # Non-current Assets
        forecast_bs["total_assets"]["non_current_assets"]["net_ppe"] = (
            net_ppe_prev - forecast_drivers["depreciation"] + forecast_drivers["capex"]
        )
        investments_prev = previous_bs["total_assets"]["non_current_assets"][
            "investments"
        ]
        forecast_bs["total_assets"]["non_current_assets"]["investments"] = (
            investments_prev + forecast_drivers["new_st_investment"]
        )

        forecast_bs["total_assets"]["non_current_assets"]["goodwill"] = previous_bs[
            "total_assets"
        ]["non_current_assets"]["goodwill"]
        forecast_bs["total_assets"]["non_current_assets"][
            "other_non_current_assets"
        ] = previous_bs["total_assets"]["non_current_assets"][
            "other_non_current_assets"
        ]

        # Current Liabilities
        forecast_bs["total_liabilities"]["current_liabilities"][
            "payables_and_accrued_expenses"
        ] = previous_bs["total_liabilities"]["current_liabilities"][
            "payables_and_accrued_expenses"
        ]
        forecast_bs["total_liabilities"]["current_liabilities"][
            "pension_and_other_postretirement_benefits"
        ] = previous_bs["total_liabilities"]["current_liabilities"][
            "pension_and_other_postretirement_benefits"
        ]
        forecast_bs["total_liabilities"]["current_liabilities"]["current_debt"] = (
            previous_bs["total_liabilities"]["current_liabilities"]["current_debt"]
        )
        forecast_bs["total_liabilities"]["current_liabilities"][
            "current_deferred_liabilities"
        ] = previous_bs["total_liabilities"]["current_liabilities"][
            "current_deferred_liabilities"
        ]
        forecast_bs["total_liabilities"]["current_liabilities"][
            "other_current_liabilities"
        ] = previous_bs["total_liabilities"]["current_liabilities"][
            "other_current_liabilities"
        ]

        # Non-current Liabilities
        long_term_debt_prev = previous_bs["total_liabilities"][
            "non_current_liabilities"
        ]["long_term_debt"]
        forecast_bs["total_liabilities"]["non_current_liabilities"][
            "long_term_debt"
        ] = (long_term_debt_prev + forecast_drivers["new_debt_needed"])
        forecast_bs["total_liabilities"]["non_current_liabilities"][
            "non_current_deferred_liabilities"
        ] = previous_bs["total_liabilities"]["non_current_liabilities"][
            "non_current_deferred_liabilities"
        ]
        forecast_bs["total_liabilities"]["non_current_liabilities"][
            "tradeand_other_payables_non_current"
        ] = previous_bs["total_liabilities"]["non_current_liabilities"][
            "tradeand_other_payables_non_current"
        ]
        forecast_bs["total_liabilities"]["non_current_liabilities"][
            "other_non_current_liabilities"
        ] = previous_bs["total_liabilities"]["non_current_liabilities"][
            "other_non_current_liabilities"
        ]

        # Equity
        forecast_bs["total_equity"]["capital_stock"] = previous_bs["total_equity"][
            "capital_stock"
        ]
        forecast_bs["total_equity"]["retained_earnings"] = (
            retained_earnings_prev
            + forecast_drivers["net_income"]
            - forecast_drivers["dividends_paid"]
        )
        forecast_bs["total_equity"]["gains_losses_not_affecting_retained_earning"] = (
            previous_bs["total_equity"]["gains_losses_not_affecting_retained_earning"]
        )

        # Validation
        total_assets = sum_dict_values(forecast_bs["total_assets"])
        total_liabilities = sum_dict_values(forecast_bs["total_liabilities"])
        total_equity = sum_dict_values(forecast_bs["total_equity"])
        balance_check = total_assets - total_liabilities - total_equity

        assert balance_check == 0, (
            f"Balance sheet does not balance for year {year_number}: {total_assets} != "
            f"{total_liabilities} + {total_equity}"
        )

        return forecast_bs, forecast_drivers


def print_balance_sheet(d, indent=0):
    for key, value in d.items():
        print(" " * indent + str(key) + ":")
        if isinstance(value, dict):
            print_balance_sheet(value, indent + 2)
        else:
            pass
            print(" " * (indent + 2) + str(value))


def main():
    msft_fs = CompanyFS("MSFT")
    # print(msft_fs.get_bs("2021-06-30"))
    # print(msft_fs.get_pnl("2021-06-30"))
    # print(msft_fs.get_cf("2021-06-30"))

    # No growth
    override_driver = {
        "sales_growth_rate": 1.0,
        "dividend_payout_ratio": 1.0,
    }
    # Forecast multiple years (3 years as an example)
    forecasted_years = msft_fs.forecast_balancesheet(
        "2021-06-30", num_years=3, override=override_driver
    )

    # Display results for each forecasted year
    for i, (forecast_bs, forecast_drivers) in enumerate(forecasted_years, 1):
        print(f"\n--- Year {i} Forecast ---")
        # print(f"Forecasted Sales: {forecast_drivers['sales']:,.0f}")
        # print(f"Forecasted Net Income: {forecast_drivers['net_income']:,.0f}")
        print(
            f"Forecasted Total Assets: {sum_dict_values(forecast_bs['total_assets']):,.0f}"
        )
        print(
            f"Forecasted Total Liabilities: {sum_dict_values(forecast_bs['total_liabilities']):,.0f}"
        )
        print(
            f"Forecasted Total Equity: {sum_dict_values(forecast_bs['total_equity']):,.0f}"
        )

        # Verify balance sheet equation
        total_assets = sum_dict_values(forecast_bs["total_assets"])
        total_liab_equity = sum_dict_values(
            forecast_bs["total_liabilities"]
        ) + sum_dict_values(forecast_bs["total_equity"])
        print(f"Balance Check (should be 0): {total_assets - total_liab_equity}")

    # Example of accessing specific years:
    print(f"\n--- Quick Access Examples ---")
    print(
        f"Year 1 Total Assets: {sum_dict_values(forecasted_years[0][0]['total_assets']):,.0f}"
    )
    print(
        f"Year 2 Total Assets: {sum_dict_values(forecasted_years[1][0]['total_assets']):,.0f}"
    )
    print(
        f"Year 3 Total Assets: {sum_dict_values(forecasted_years[2][0]['total_assets']):,.0f}"
    )


if __name__ == "__main__":
    main()
