from mcp.server.fastmcp import FastMCP
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io
import base64
from ta.trend import SMAIndicator, MACD
from ta.momentum import RSIIndicator

# Initialize FastMCP server
class YFinanceMCP:
    def __init__(self):
        self.mcp = FastMCP("yfinance-analyst")
        self.setup_tools()
        
    def setup_tools(self):
        # Company Information Tools
        @self.mcp.tool()
        def get_company_info(ticker: str) -> dict:
            """
            Get comprehensive information about a company.
            
            Args:
                ticker (str): The stock ticker symbol
                
            Returns:
                dict: Detailed company information
            """
            try:
                company = yf.Ticker(ticker)
                info = company.info
                relevant_info = {
                    "name": info.get("longName", ""),
                    "sector": info.get("sector", ""),
                    "industry": info.get("industry", ""),
                    "website": info.get("website", ""),
                    "description": info.get("longBusinessSummary", ""),
                    "country": info.get("country", ""),
                    "employees": info.get("fullTimeEmployees", ""),
                    "market_cap": info.get("marketCap", ""),
                    "pe_ratio": info.get("trailingPE", ""),
                    "forward_pe": info.get("forwardPE", ""),
                    "dividend_rate": info.get("dividendRate", ""),
                    "dividend_yield": info.get("dividendYield", ""),
                    "beta": info.get("beta", ""),
                    "52_week_high": info.get("fiftyTwoWeekHigh", ""),
                    "52_week_low": info.get("fiftyTwoWeekLow", "")
                }
                return relevant_info
            except Exception as e:
                return {"error": str(e)}
                
        @self.mcp.tool()
        def get_financials(ticker: str, statement_type: str = "income") -> dict:
            """
            Get financial statements for a company.
            
            Args:
                ticker (str): The stock ticker symbol
                statement_type (str): Type of financial statement - "income", "balance", "cash" 
                
            Returns:
                dict: Financial statement data
            """
            try:
                company = yf.Ticker(ticker)
                if statement_type.lower() == "income":
                    return company.income_stmt.to_dict()
                elif statement_type.lower() == "balance":
                    return company.balance_sheet.to_dict()
                elif statement_type.lower() == "cash":
                    return company.cashflow.to_dict()
                else:
                    return {"error": "Invalid statement type. Use 'income', 'balance', or 'cash'."}
            except Exception as e:
                return {"error": str(e)}
                
        @self.mcp.tool()
        def get_institutional_holders(ticker: str) -> dict:
            """
            Get information about institutional holders of a stock.
            
            Args:
                ticker (str): The stock ticker symbol
                
            Returns:
                dict: Information about institutional holdings
            """
            try:
                company = yf.Ticker(ticker)
                holders = company.institutional_holders
                return holders.to_dict() if holders is not None else {}
            except Exception as e:
                return {"error": str(e)}
        
        # Additional tools implementation continues...
        
        # Market Data Tools
        @self.mcp.tool()
        def get_current_price(tickers: str) -> dict:
            """
            Get current price and trading information for one or more stocks.
            
            Args:
                tickers (str): Comma-separated stock ticker symbols
                
            Returns:
                dict: Current price data for each ticker
            """
            try:
                ticker_list = [t.strip() for t in tickers.split(',')]
                result = {}
                
                for ticker in ticker_list:
                    stock = yf.Ticker(ticker)
                    quote = stock.info
                    result[ticker] = {
                        "price": quote.get("currentPrice", None) or quote.get("regularMarketPrice", None),
                        "change": quote.get("regularMarketChange", None),
                        "change_percent": quote.get("regularMarketChangePercent", None),
                        "volume": quote.get("regularMarketVolume", None),
                        "day_high": quote.get("regularMarketDayHigh", None),
                        "day_low": quote.get("regularMarketDayLow", None),
                        "market_cap": quote.get("marketCap", None)
                    }
                return result
            except Exception as e:
                return {"error": str(e)}
                
        @self.mcp.tool()
        def get_historical_data(ticker: str, period: str = "1y", interval: str = "1d") -> dict:
            """
            Get historical price data for a stock.
            
            Args:
                ticker (str): The stock ticker symbol
                period (str): Period of time (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
                interval (str): Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
                
            Returns:
                dict: Historical price data
            """
            try:
                data = yf.download(ticker, period=period, interval=interval, progress=False)
                return data.to_dict()
            except Exception as e:
                return {"error": str(e)}
        
        # Technical Analysis Tools
        @self.mcp.tool()
        def calculate_technical_indicators(ticker: str, period: str = "1y") -> dict:
            """
            Calculate key technical indicators for a stock.
            
            Args:
                ticker (str): The stock ticker symbol
                period (str): Period of time
                
            Returns:
                dict: Technical indicators data
            """
            try:
                # Get historical data
                data = yf.download(ticker, period=period, progress=False)
                
                # Calculate indicators
                data['SMA_20'] = SMAIndicator(data['Close'], window=20).sma_indicator()
                data['SMA_50'] = SMAIndicator(data['Close'], window=50).sma_indicator()
                data['SMA_200'] = SMAIndicator(data['Close'], window=200).sma_indicator()
                
                # MACD
                macd = MACD(data['Close'])
                data['MACD'] = macd.macd()
                data['MACD_Signal'] = macd.macd_signal()
                data['MACD_Histogram'] = macd.macd_diff()
                
                # RSI
                data['RSI'] = RSIIndicator(data['Close']).rsi()
                
                # Volume analysis
                if len(data) >= 20:
                    data['Volume_20MA'] = data['Volume'].rolling(window=20).mean()
                
                # Trend status
                latest = data.iloc[-1]
                
                trend_status = {
                    "price": latest['Close'],
                    "above_20sma": latest['Close'] > latest['SMA_20'],
                    "above_50sma": latest['Close'] > latest['SMA_50'],
                    "above_200sma": latest['Close'] > latest['SMA_200'],
                    "20_50_bullish": latest['SMA_20'] > latest['SMA_50'],
                    "50_200_bullish": latest['SMA_50'] > latest['SMA_200'],
                    "rsi": latest['RSI'],
                    "macd_bullish": latest['MACD'] > latest['MACD_Signal'],
                }
                
                return {
                    "indicators": data.tail(50).to_dict(),
                    "trend_analysis": trend_status
                }
            except Exception as e:
                return {"error": str(e)}
        
        # Report Generation Tools
        @self.mcp.tool()
        def generate_stock_report(ticker: str) -> dict:
            """
            Generate a comprehensive stock analysis report.
            
            Args:
                ticker (str): The stock ticker symbol
                
            Returns:
                dict: Comprehensive stock report data
            """
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                hist = yf.download(ticker, period="1y", progress=False)
                
                # Calculate key metrics
                current_price = hist['Close'].iloc[-1]
                week_ago_price = hist['Close'].iloc[-5] if len(hist) >= 5 else hist['Close'].iloc[0]
                month_ago_price = hist['Close'].iloc[-22] if len(hist) >= 22 else hist['Close'].iloc[0]
                year_ago_price = hist['Close'].iloc[0]
                
                week_return = (current_price / week_ago_price - 1) * 100
                month_return = (current_price / month_ago_price - 1) * 100
                year_return = (current_price / year_ago_price - 1) * 100
                
                # Calculate volatility
                returns = hist['Close'].pct_change().dropna()
                volatility = returns.std() * (252 ** 0.5)  # Annualized
                
                # Technical indicators
                hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
                hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
                hist['SMA_200'] = hist['Close'].rolling(window=200).mean()
                
                # Latest values
                latest = hist.iloc[-1]
                
                # Technical status
                tech_status = {
                    "above_20sma": latest['Close'] > latest['SMA_20'] if not pd.isna(latest['SMA_20']) else None,
                    "above_50sma": latest['Close'] > latest['SMA_50'] if not pd.isna(latest['SMA_50']) else None,
                    "above_200sma": latest['Close'] > latest['SMA_200'] if not pd.isna(latest['SMA_200']) else None,
                    "20_50_bullish": latest['SMA_20'] > latest['SMA_50'] if not pd.isna(latest['SMA_20']) and not pd.isna(latest['SMA_50']) else None,
                    "50_200_bullish": latest['SMA_50'] > latest['SMA_200'] if not pd.isna(latest['SMA_50']) and not pd.isna(latest['SMA_200']) else None
                }
                
                # Get news
                try:
                    search = yf.Search(ticker, news_count=5)
                    news = search.news
                except:
                    news = []
                
                # Compile report
                report = {
                    "company_info": {
                        "name": info.get("longName", ticker),
                        "sector": info.get("sector", ""),
                        "industry": info.get("industry", ""),
                        "website": info.get("website", ""),
                        "description": info.get("longBusinessSummary", "")
                    },
                    "price_data": {
                        "current_price": current_price,
                        "52_week_high": info.get("fiftyTwoWeekHigh", ""),
                        "52_week_low": info.get("fiftyTwoWeekLow", ""),
                        "average_volume": info.get("averageVolume", ""),
                        "market_cap": info.get("marketCap", "")
                    },
                    "performance": {
                        "week_return": week_return,
                        "month_return": month_return,
                        "year_return": year_return,
                        "volatility": volatility
                    },
                    "valuation": {
                        "pe_ratio": info.get("trailingPE", ""),
                        "forward_pe": info.get("forwardPE", ""),
                        "peg_ratio": info.get("pegRatio", ""),
                        "price_to_sales": info.get("priceToSalesTrailing12Months", ""),
                        "price_to_book": info.get("priceToBook", ""),
                    },
                    "technical_status": tech_status,
                    "news": [{"title": item.get("title", ""), "link": item.get("link", "")} for item in news[:5]]
                }
                
                return report
            except Exception as e:
                return {"error": str(e)}
        
        # Additional methods would continue here...
            
    def run(self):
        self.mcp.run(transport='stdio')

if __name__ == "__main__":
    server = YFinanceMCP()
    server.run()
