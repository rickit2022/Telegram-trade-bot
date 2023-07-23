import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates 
import requests, json, os, logging
from datetime import datetime, timedelta

data_logger = logging.getLogger('data')
data_logger.setLevel(logging.ERROR)
handler = logging.FileHandler('bot/logs/data.log')
handler.setLevel(logging.ERROR)
handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
data_logger.addHandler(handler)

def write_data(data, filename ,dir = None):
        path = filename
        if dir:
            path = f"{dir}/{filename}"

        try:
            with open(path, "w") as f:
                if ".json" in path:
                    f.write(json.dumps(data))
                elif ".csv" in path:
                    f.write(data.to_csv())
                elif ".txt" in path:
                    f.write(data)
        except Exception as e:
            data_logger.error(f"Export-error: \n {e}")

def get_data_df(filename, dir = None):
    path = filename
    if dir:
        path = f"{dir}/{filename}"

    with open(f"bot/{path}.json", "r") as f:
        data = json.load(f)
        return pd.DataFrame(data['data'])

def read_data(filename, dir = None):
    path = filename
    if dir:
        path = f"{dir}/{filename}"

    with open(f"bot/{path}.txt", "r") as f:
        data = f.read()
        return data
    
def get_today():
    return datetime.now().date()

def message_parser(message) -> list:
    """Parse requests in the message text"""
    var_dict = {}
    ticker, params = message.split(None, 2)[1:]

    arg_list = params.split(',')
    for args in arg_list:
        arg, value = args.strip().split('=')
        var_dict[arg.strip()] = value.strip()

    return ticker,var_dict

def visualise(data, filename, type=None, zoom = None):
    path = f"bot/resources/charts/{filename}.png"
    if os.path.exists(path):
        os.remove(path)
    if zoom is None:
        zoom = 1

    data['date-month'] = pd.to_datetime(data['date'])
    try:
        if type == "line":
            sns.set_style("darkgrid")
            sns.set(rc={'figure.figsize':(16/float(zoom),9/float(zoom))})
            sns.lineplot(data=data, x="date-month", y="close")
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m'))
            plt.xticks(data['date-month'], rotation=45)

            plt.title(f"{filename}'s close price trend", fontsize= 16)
            plt.xlabel('Date', fontweight='bold')
            plt.ylabel('Closing price', fontweight='bold')

            plt.savefig(path, dpi=300)
            plt.clf()
            plt.close()
        return path
    except Exception as e:
        data_logger.error(f"Visualise-error\n{e}")
    return None

def get_symbol_history(symbol, start = None, end = None, interval = None):
    FINFO_VNDIRECT = 'https://finfo-api.vndirect.com.vn/v4/stock_prices/'
    if not start:
        start = (get_today() - timedelta(days= int(interval))).strftime("%Y-%m-%d")
    if not end:
        end = get_today().strftime("%Y-%m-%d")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
    } 
    query = 'code:' + symbol + '~date:gte:' + start + '~date:lte:' + end
    delta = datetime.strptime(end, '%Y-%m-%d') - datetime.strptime(start, '%Y-%m-%d')
    params = {
        "sort": "date",
        "size": delta.days + 1,
        "page": 1,
        "q": query
    }
    response = requests.get(FINFO_VNDIRECT, headers=headers, params=params).json()

    df = pd.DataFrame(response['data'])

    write_data(response, f"{symbol}.json", "resources/requests")
    write_data(df.to_string(index= False), f"{symbol}.txt", "resources/requests")
    return df

def get_symbol_realtime(symbol):
    pass