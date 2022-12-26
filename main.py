import platform
import aiohttp
import asyncio
from datetime import datetime, timedelta


async def main(days: int):
    results = []
    async with aiohttp.ClientSession() as session:
        for i in range(days):
            # Calculate the date for the request
            date = (datetime.now() - timedelta(days=i) -
                    timedelta(days=1)).strftime('%d.%m.%Y')
            # Make the request
            async with session.get(f'https://api.privatbank.ua/p24api/exchange_rates?json&date={date}') as response:
                result = await response.json()
                rates = {}
                for rate in result["exchangeRate"]:
                    if rate["currency"] == "USD":
                        rates["USD"] = {"sale": rate["saleRate"],
                                        "purchase": rate["purchaseRate"]}
                    if rate["currency"] == "EUR":
                        rates["EUR"] = {"sale": rate["saleRate"],
                                        "purchase": rate["purchaseRate"]}
                results.append({date: rates})
    return results


async def handle_client(reader, writer):
    # Read the data from the client
    data = await reader.read()
    # Decode the data as a string
    days_str = data.decode()
    # Check if the input is a valid number of days
    try:
        days = int(days_str)
        if days < 1 or days > 10:
            raise ValueError
    except ValueError:
        # Send an error message to the client if the input is not a valid number of days
        writer.write(
            "Error: Please enter a number of days between 1 and 10".encode())
        await writer.drain()
    else:
        # Get the exchange rates
        rates = await main(days)
        # Encode the rates as bytes and write them to the client
        writer.write(str(rates).encode())
        await writer.drain()
    finally:
        # Close the connection
        writer.close()


async def start_server():
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Create the server
    server = await asyncio.start_server(handle_client, 'localhost', 8000)
    # Run the server until it is cancelled
    await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(start_server())
