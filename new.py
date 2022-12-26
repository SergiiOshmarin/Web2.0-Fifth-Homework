import aiohttp
import asyncio
import argparse
from typing import List
import websockets
import requests

class ExchangeRateClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def get_exchange_rates(self, date: str, currencies: List[str]) -> dict:
        """
        Get the exchange rates for the specified date and currencies.
        
        Parameters:
        - date: The date to get the exchange rates for, in the format "DD.MM.YYYY".
        - currencies: The list of currencies to get the exchange rates for.
        
        Returns:
        A dictionary with the exchange rates for each currency.
        """
        # Construct the URL
        url = f"{self.base_url}/exchange_rates?date={date}"
        # Add the currencies as a comma-separated list to the query string
        params = {"currency": ",".join(currencies)}
        # Make the GET request
        resp = requests.get(url, params=params)
        # Check if the request was successful
        if resp.status_code == 200:
            data = resp.json()
            # Parse the response data and return the exchange rates for the specified currencies
            result = {}
            for rate in data["exchangeRate"]:
                result[rate["currency"]] = rate
            return result
        else:
            raise Exception("Failed to get exchange rates")

async def chat_server(websocket, path):
    """
    Chat server that handles messages from websocket clients.
    """
    try:
        async for message in websocket:
            # Split the message into command and arguments
            parts = message.split()
            command = parts[0]
            args = parts[1:]

            # Handle the exchange command
            if command == "exchange":
                # Create the exchange rate client
                client = ExchangeRateClient("https://api.privatbank.ua/p24api")

                # Get the exchange rates
                date = args[0]
                currencies = args[1:]
                exchange_rates = await client.get_exchange_rates(date, currencies)

                # Format the exchange rates as a message and send it to the client
                message = ""
                for currency, rate in exchange_rates.items():
                    message += f"{currency}:\n"
                    for key, value in rate.items():
                        message += f"{key}: {value}\n"
                await websocket.send(message)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Start the chat server
    start_server = websockets.serve(chat_server, "localhost", 8000)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()