import asyncio
import aiohttp
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots


API_KEY = "O8CWLHU7WK70K5U8"  # Replace with your Alpha Vantage API key


async def fetch_and_validate(session, url, data_type):
    """Asynchronously fetch and validate API response"""
    try:
        async with session.get(url) as response:
            response_json = await response.json()
            if 'annualReports' not in response_json and data_type != 'overview' and 'Time Series (Daily)' not in response_json and data_type != 'price':
                print(f"Error in {data_type} response: {response_json}")
                raise KeyError(f'annualReports or Time Series (Daily) not in {data_type} response')
            return response_json
    except Exception as e:
        print(f"Error fetching {data_type} data: {str(e)}")
        return None


async def get_financial_data_async(ticker):
    """Asynchronously fetch financial data using Alpha Vantage API"""
    async with aiohttp.ClientSession() as session:
        urls = {
            "income": f"https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={ticker}&apikey={API_KEY}",
            "balance": f"https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={ticker}&apikey={API_KEY}",
            "cash": f"https://www.alphavantage.co/query?function=CASH_FLOW&symbol={ticker}&apikey={API_KEY}",
            "overview": f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={API_KEY}",
            "price": f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={API_KEY}&outputsize=full"
        }

        tasks = {
            data_type: fetch_and_validate(session, url, data_type)
            for data_type, url in urls.items()
        }

        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        financial_data_json = dict(zip(tasks.keys(), results))

        financial_data = {}
        for data_type, json_response in financial_data_json.items():
            if json_response and not isinstance(json_response, Exception):
                if data_type in ['income', 'balance', 'cash']:
                    financial_data[data_type] = pd.DataFrame(json_response.get('annualReports', []))
                elif data_type == 'overview':
                    if 'Symbol' in json_response:
                        financial_data[data_type] = json_response
                    else:
                        print(f"Error in overview response: {json_response}")
                        return None #Handle overview error specifically
                elif data_type == 'price':
                    if 'Time Series (Daily)' in json_response:
                        financial_data[data_type] = pd.DataFrame(json_response.get('Time Series (Daily)', {})).T
                    else:
                        print(f"Error in price response: {json_response}")
                        return None #Handle price error specifically
            else:
                print(f"Failed to fetch {data_type} data.")
                return None #Return None if any data fetch fails

        return financial_data


def calculate_key_metrics(financial_data):
    """Calculate important financial ratios and metrics"""
    if not financial_data:
        return None

    inc = financial_data['income'].copy()
    bs = financial_data['balance'].copy()
    overview = financial_data['overview']

    income_exclude_cols = ['fiscalDateEnding', 'reportedCurrency']
    balance_exclude_cols = ['fiscalDateEnding', 'reportedCurrency']

    inc_numeric_cols = [col for col in inc.columns if col not in income_exclude_cols]
    bs_numeric_cols = [col for col in bs.columns if col not in balance_exclude_cols]

    inc[inc_numeric_cols] = inc[inc_numeric_cols].replace('None', np.nan).astype(float)
    bs[bs_numeric_cols] = bs[bs_numeric_cols].replace('None', np.nan).astype(float)

    metrics = {
        'PE_Ratio': float(overview.get('PERatio', np.nan)) if overview.get('PERatio') not in [None, 'None'] else np.nan,
        'PB_Ratio': float(overview.get('PriceToBookRatio', np.nan)) if overview.get('PriceToBookRatio') not in [None, 'None'] else np.nan,
        'Debt_to_Equity': (bs['totalLiabilities'].iloc[0] / bs['totalShareholderEquity'].iloc[0]
                           if not pd.isna(bs['totalLiabilities'].iloc[0]) and not pd.isna(
            bs['totalShareholderEquity'].iloc[0]) else np.nan),
        'Current_Ratio': (bs['totalCurrentAssets'].iloc[0] / bs['totalCurrentLiabilities'].iloc[0]
                          if not pd.isna(bs['totalCurrentAssets'].iloc[0]) and not pd.isna(
            bs['totalCurrentLiabilities'].iloc[0]) else np.nan),
        'ROE': (inc['netIncome'].iloc[0] / bs['totalShareholderEquity'].iloc[0]
                if not pd.isna(inc['netIncome'].iloc[0]) and not pd.isna(
            bs['totalShareholderEquity'].iloc[0]) else np.nan),
        'Gross_Margin': (inc['grossProfit'].iloc[0] / inc['totalRevenue'].iloc[0]
                         if not pd.isna(inc['grossProfit'].iloc[0]) and not pd.isna(
            inc['totalRevenue'].iloc[0]) else np.nan),
        'EPS': float(overview.get('EPS', np.nan)) if overview.get('EPS') not in [None, 'None'] else np.nan,
        'Dividend_Yield': float(overview.get('DividendYield', np.nan)) * 100 if overview.get('DividendYield') not in [None, 'None'] else np.nan
    }

    financial_data['income'] = inc
    financial_data['balance'] = bs

    return metrics


def create_visualizations(ticker, financial_data, metrics):
    """Create comprehensive visualizations of the financial data"""
    if not financial_data or not metrics:
        return None

    fig = make_subplots(rows=2, cols=2,
                        subplot_titles=('Revenue & Net Income', 'Key Ratios',
                                        'Balance Sheet Composition', 'Stock Price History'),
                        vertical_spacing=0.15,
                        specs=[[{'type': 'xy'}, {'type': 'xy'}],
                               [{'type': 'domain'}, {'type': 'xy'}]]) # Set subplot type to 'domain' for pie chart


    inc = financial_data['income']
    years = inc['fiscalDateEnding'].str[:4]
    revenue = inc['totalRevenue'] / 1e9
    net_income = inc['netIncome'] / 1e9

    fig.add_trace(go.Bar(x=years, y=revenue, name='Revenue ($B)'), row=1, col=1)
    fig.add_trace(go.Scatter(x=years, y=net_income, name='Net Income ($B)',
                             mode='lines+markers'), row=1, col=1)

    ratio_names = ['PE_Ratio', 'PB_Ratio', 'Debt_to_Equity', 'Current_Ratio']
    ratio_values = [metrics[ratio] for ratio in ratio_names]

    fig.add_trace(go.Bar(x=ratio_names, y=ratio_values, name='Ratios'), row=1, col=2)

    bs = financial_data['balance']
    bs_components = {
        'Assets': bs['totalAssets'].iloc[0] / 1e9 if not pd.isna(bs['totalAssets'].iloc[0]) else 0,
        'Liabilities': bs['totalLiabilities'].iloc[0] / 1e9 if not pd.isna(bs['totalLiabilities'].iloc[0]) else 0,
        'Equity': bs['totalShareholderEquity'].iloc[0] / 1e9 if not pd.isna(bs['totalShareholderEquity'].iloc[0]) else 0
    }

    fig.add_trace(go.Pie(labels=list(bs_components.keys()),
                         values=list(bs_components.values()),
                         name='Balance Sheet ($B)'), row=2, col=1) # Pie chart in row 2, col 1

    price = financial_data['price']
    price.index = pd.to_datetime(price.index)
    price_5y = price[price.index > price.index.max() - pd.Timedelta(days=5 * 365)]
    fig.add_trace(go.Scatter(x=price_5y.index, y=price_5y['4. close'].astype(float),
                             name='Stock Price', mode='lines'), row=2, col=2)

    fig.update_layout(
        height=800,
        width=1200,
        title_text=f"Financial Analysis for {ticker} - {datetime.now().strftime('%Y-%m-%d')}",
        showlegend=True,
        template='plotly_white'
    )

    return fig


def analyze_company(ticker):
    """Main function to analyze a company's financials"""
    print(f"Analyzing {ticker}...")

    financial_data = asyncio.run(get_financial_data_async(ticker)) # Use asynchronous data fetching
    if not financial_data:
        return "Failed to fetch financial data"

    metrics = calculate_key_metrics(financial_data)
    if not metrics:
        return "Failed to calculate metrics"

    print("\nCompany Overview:")
    print(f"Name: {financial_data['overview'].get('Name', 'N/A')}")
    print(f"Sector: {financial_data['overview'].get('Sector', 'N/A')}")
    print(f"Market Cap: ${float(financial_data['overview'].get('MarketCapitalization', 0)):,}")

    print("\nKey Financial Metrics:")
    for metric, value in metrics.items():
        if not pd.isna(value):
            print(f"{metric.replace('_', ' ')}: {value:.2f}")

    print("\nValue Investing Assessment:")
    if metrics['PE_Ratio'] < 15 and not pd.isna(metrics['PE_Ratio']):
        print("- P/E Ratio suggests potential undervaluation")
    if metrics['PB_Ratio'] < 1.5 and not pd.isna(metrics['PB_Ratio']):
        print("- P/B Ratio indicates possible value opportunity")
    if metrics['Debt_to_Equity'] < 1 and not pd.isna(metrics['Debt_to_Equity']):
        print("- Healthy Debt-to-Equity ratio")
    if metrics['Current_Ratio'] > 1.5 and not pd.isna(metrics['Current_Ratio']):
        print("- Strong liquidity position")

    fig = create_visualizations(ticker, financial_data, metrics)
    if fig:
        fig.show()

    return "Analysis complete"


def main():
    """Main execution function"""
    print("Welcome to the Value Investing Analyzer!")
    print("Note: Uses Alpha Vantage API - rate limited to 5 calls/minute")
    ticker = input("Please enter a stock ticker symbol (e.g., AAPL): ").upper()
    result = analyze_company(ticker)
    print(result)


if __name__ == "__main__":
    # Required libraries: pip install requests pandas matplotlib plotly numpy aiohttp asyncio
    API_KEY = "O8CWLHU7WK70K5U8"
    if API_KEY == "YOUR_API_KEY_HERE":
        print("Please replace API_KEY with your Alpha Vantage API key")
    else:
        main()