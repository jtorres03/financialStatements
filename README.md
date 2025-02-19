# Value Investing Analyzer

## Description

This Python script is a tool for analyzing the financial health of publicly traded companies, focusing on value investing principles. It fetches financial data from the Alpha Vantage API, calculates key financial metrics and ratios, performs a basic value investing assessment, and generates visualizations to help understand the company's financial standing.

## Features

*   **Data Fetching:** Retrieves financial data (Income Statement, Balance Sheet, Cash Flow, Overview, and Daily Stock Prices) from the Alpha Vantage API.
*   **Key Metric Calculation:** Calculates important financial ratios such as:
    *   P/E Ratio
    *   P/B Ratio
    *   Debt-to-Equity Ratio
    *   Current Ratio
    *   Return on Equity (ROE)
    *   Gross Margin
    *   Earnings Per Share (EPS)
    *   Dividend Yield
*   **Value Investing Assessment:** Provides a basic assessment based on common value investing criteria, such as P/E Ratio, P/B Ratio, Debt-to-Equity Ratio, and Current Ratio, to identify potentially undervalued stocks.
*   **Visualizations:** Generates comprehensive visualizations using Plotly, including:
    *   Revenue and Net Income Bar and Line chart
    *   Key Ratios Bar chart
    *   Balance Sheet Composition Bar chart
    *   Stock Price History Line chart (5-year)
*   **Asynchronous API Requests:** Implements asynchronous HTTP requests using `aiohttp` and `asyncio` for efficient data fetching, reducing overall execution time.

## Installation

Before running the script, ensure you have Python installed and the required libraries.

1.  **Clone the repository (if applicable) or save the Python script (`FinancialSummaries.py`) to your local machine.**

2.  **Create a virtual environment (recommended):**


3.  **Install required Python libraries:**

    ```bash
    pip install requests pandas matplotlib plotly numpy aiohttp asyncio
    ```

## Usage

1.  **Obtain an Alpha Vantage API Key:**
    *   Sign up for a free API key at [Alpha Vantage](https://www.alphavantage.co/).
    *   Replace `"YourAPIKEY"` in the `FinancialSummaries.py` script with your actual API key.

2.  **Run the script:**

    ```bash
    python FinancialSummaries.py
    ```

3.  **Enter Stock Ticker Symbol:**
    *   When prompted, enter the stock ticker symbol of the company you want to analyze (e.g., `AAPL`, `MSFT`, `GOOG`). The script will then fetch the financial data and perform the analysis.

## API Key and Rate Limits

*   **Alpha Vantage API Key:** This script relies on the Alpha Vantage API to fetch financial data. You need to obtain a free API key from their website ([Alpha Vantage](https://www.alphavantage.co/)) and insert it into the script.
*   **Rate Limits:** The Alpha Vantage Free API is rate-limited. Be mindful of these limits when using the script, especially if analyzing multiple companies in quick succession. If you exceed the rate limit, you may need to wait before running the script again.

## Output

The script will output the following information to the console:

*   **Company Overview:** Name, Sector, and Market Capitalization.
*   **Key Financial Metrics:** Calculated financial ratios and metrics.
*   **Value Investing Assessment:** A brief assessment based on value investing principles.
*   **Visualizations:**  A set of interactive plots will be displayed in your default web browser, including:
    *   Revenue & Net Income chart
    *   Key Ratios chart
    *   Balance Sheet Composition chart
    *   Stock Price History chart

## Libraries Used

*   **requests:** For making HTTP requests to the Alpha Vantage API.
*   **pandas:** For data manipulation and analysis, especially for handling financial data in DataFrames.
*   **numpy:** For numerical operations.
*   **datetime:** For handling dates and timestamps.
*   **plotly:** For creating interactive visualizations.
*   **aiohttp & asyncio:** For asynchronous HTTP requests to improve efficiency.

## Disclaimer

This script is for informational and educational purposes only and should not be considered financial advice.
