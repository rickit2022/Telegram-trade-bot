import bot.bot as bot
from utils import write_data
from credsManager import get_secret, get_key
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass

if __name__ == "__main__":
    if not get_secret():
        exit()
    bot.run()