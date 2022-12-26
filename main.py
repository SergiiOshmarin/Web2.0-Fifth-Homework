import asyncio
import logging
import websockets
import aiohttp
import argparse
from datetime import datetime, timedelta
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK

logging.basicConfig(level=logging.INFO)


async def api(days: int):
    results = []
    async with aiohttp.ClientSession() as session:
        for i in range(days):
            # Calculate the date for the request
            date = (datetime.now() - timedelta(days=i)).strftime('%d.%m.%Y')
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


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distribute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def distribute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            # Check if the input is a valid number of days
            try:
                days = int(message)
                if days < 1 or days > 10:
                    raise ValueError
            except ValueError:
                # Send an error message to the client if the input is not a valid number of days
                await ws.send("Error: Please enter a number of days between 1 and 10")
            except Exception:
                # Send an error message to the client if the input is not a valid number
                await ws.send("Error: Please enter a valid number")
            else:
                # Get the exchange rates
                rates = await api(days)
                # Encode the rates as bytes and write them to the client
                await ws.send(str(rates))

async def main(*argv):
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8000):
        # Use the command line argument for the number of days if provided,
        # otherwise run the server indefinitely
        try:
            days = int(argv[0])
            if days < 1 or days > 10:
                raise ValueError
        except (TypeError,IndexError, ValueError):
            print("Please go to server and type correct number from 1 to 10")
            await asyncio.Future()
        else:
            # Get the exchange rates
            rates = await api(days)
            # Encode the rates as bytes and write them to the client
            print(str(rates))
            print("Now you can try local server and type correct number from 1 to 10, and presss Exchange button")
            await asyncio.Future()


if __name__ == '__main__':
    # Parse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("days", nargs="?", type=int, help="number of days for which to get the exchange rates")
    args = parser.parse_args()
    asyncio.run(main(args.days))

