from mcp.server.fastmcp import FastMCP
import yfinance as yf


if __name__ == "__main__":
    # Initialize FastMCP server
    mcp = FastMCP("yfinance")

    @mcp.tool()
    def get_info(company: str) -> str:
        """
        Retrieve information about a given company using its stock ticker.

        Args:
            company (str): The stock ticker for the company to retrieve information about.

        Returns:
            str: Detailed information about the company.
        """
        # Create a Ticker object for the given company
        dat = yf.Ticker(company)

        # Retrieve and return information about the company
        return dat.get_info()

    @mcp.tool()
    def get_news(company: str) -> str:
        """
        Get the latest news for a given company.

        Args:
            company (str): The stock ticker for the company to search for.

        Returns:
            str: The latest news articles for the given company.
        """

        return yf.Search(company, news_count=10,).news


    @mcp.tool()
    def get_price_history(
        company: str,
        start_date: str,
        end_date: str
    ) -> str:
        """
        Get the price history for a given company.

        Args:
            company (str): The stock ticker for the company to retrieve its price history about.
            start_date (str): The start date for the price history, in the format of "YYYY-MM-DD".
            end_date (str): The end date for the price history, in the format of "YYYY-MM-DD".

        Returns:
            str: The price history for the given company during the given time period.
        """
        # Use Yahoo Finance to download the price history
        # for the given company in the given time period
        return yf.download(company, start=start_date, end=end_date)

    # Run the server
    mcp.run(transport='stdio')
