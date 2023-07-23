[![Live demo-bot](https://bit.ly/450G84R)](https://t.me/Akira_yourService_bot)

# Trading-Bot
A bot that simplifies the process of trading through 
chat-friendly interface on Telegram. This code utilises
several trading broker's APIs, including Alpaca's REST API,
websockets and SSE to get historical and real-time stock market 
data such as open, close, volume, net change, etc. in both VN and US
equties.

## FEATURES
### Stocks
- Get a stock historical data by ticker (symbol)
- Create a chart (line, bar, pie) of a stock's price trend by ticker (symbol)
- Connect to a trading account
- Place an order (buy/sell)
### Songs
- Search and play a song by name
- Play a random song

## Example usage


## INSTALLATION
If you want to run the bot locally, you need to first set up Google Cloud Platform's 
[Secrets Manager](https://cloud.google.com/secret-manager/docs/configuring-secret-manager) 
and [ADC](https://cloud.google.com/docs/authentication/provide-credentials-adc), then: 
- Clone this repo
- Install required dependencies can be installed through PyPi: `pip -install -r requirements.txt`
- Setup relevant API keys in creds.json
- Navigate to the root directory and run main.py. 

To host your own bot, look through the host-your-bot guide section below.

Alternatively, if want to try the bot, click [here](https://t.me/Akira_yourService_bot) to start chatting on telegram.