import asyncio
import websockets
import requests
import json

# Constants for Binance API
STREAM_URL = "wss://stream.binance.com:9443/ws/btcusdt@depth"
ORDER_BOOK_URL = "https://api.binance.com/api/v3/depth"
SYMBOL = "BTCUSDT"
LIMIT = 1000  # Use max depth for snapshot


class BinanceSpotMarketDataStream:
    def __init__(self, symbol, orderbook, limit=LIMIT):
        self.symbol = symbol
        self.orderbook = orderbook
        self.limit = limit
        self.last_update_id = None
        return

    async def initialize(self):
        response = requests.get(ORDER_BOOK_URL, params={"symbol": self.symbol, "limit": self.limit})
        snapshot = response.json()
        
        self.last_update_id = snapshot['lastUpdateId']
        return snapshot

    async def update(self):
        
        snapshot = await self.initialize()
        print(snapshot)

        async with websockets.connect(STREAM_URL) as ws:

            print("Connected to Binance WebSocket depth stream")

            while True:
                message = await ws.recv()
                data = json.loads(message)

                if data['u'] <= self.last_update_id:
                    continue

                if data['U'] <= self.last_update_id + 1 <= data['u']:
                    yield data

                self.last_update_id = data['u']
            return

    async def run(self):
        async for payload in self.update():
            print(payload)

        return


orderbook = OrderBook()
order_book = BinanceSpotMarketDataStream(SYMBOL, orderbook)

asyncio.run(order_book.run())
