import datetime as dt
import requests


URL = f"https://www.nseindia.com/api/option-chain-indices"
MARKET_URL = "https://www.nseindia.com/api/marketStatus"
INDICES_URL = "https://www.nseindia.com/api/allIndices"


headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/80.0.3987.149 Safari/537.36',
    'accept-language': 'en,gu;q=0.9,hi;q=0.8',
    'accept-encoding': 'gzip, deflate, br'
}


def get_atm_strike(nifty_cmp):
    
    atm_strike = (nifty_cmp // 50) * 50
    
    if nifty_cmp % 50 > 25:
        atm_strike += 50
    
    return int(atm_strike)


def get_required_strikes(nifty_cmp:float, available_strikes:list, strike_range:int=800):
    
    atm_strike = get_atm_strike(nifty_cmp)
    
    return [
        strike 
        for strike in available_strikes
        if (strike > atm_strike - strike_range) and (strike < atm_strike + strike_range)
    ]


def fetch_oi(index_name:str):

    symbol = {
        'symbol': index_name
    }
    response = requests.get(URL, params=symbol, headers=headers)

    if response.status_code == 200:

        data = response.json()
        filtered_data = data['filtered']

        market_data = requests.get(MARKET_URL, headers=headers)
        market_data = market_data.json()
        market_data = [r for r in market_data['marketState'] if r['index']=="NIFTY 50"][0]

        # index_data = requests.get(INDICES_URL, headers=headers)
        # index_data = index_data.json()

        # if index_name == "NIFTY":
        #     index = "NIFTY 50"
        # elif index_name == "BANKNIFTY":
        #     index = "NIFTY BANK"

        # index_data = [r for r in index_data['data'] if r['index']==index][0]

        # vix_data = [r for r in index_data['data'] if r['index'] == 'INDIA VIX'][0]

        final_data = {
            **market_data,
            **filtered_data,
            # **index_data,
            # **vix_data
        }

        available_strikes = [d['strikePrice'] for d in final_data['data']]
        index_cmp = market_data['last']

        atm_strike = get_atm_strike(index_cmp)
        required_strikes = get_required_strikes(index_cmp, available_strikes)

        final_data['data'] = [d for d in final_data['data'] if d['CE']['strikePrice'] in required_strikes]

        return {
            'status': 'ok',
            'timestamp': dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'strikes': required_strikes,
            'atm_strike': atm_strike,
            **final_data
        }
    
    else:

        return {
            'status': 'error',
            'message': response.text
        }



def get_strike_and_expiry_dates():

    data = fetch_oi()

    return {
        'strikes': data['strikes'],
        'atm_strike': data['atm_strike'],
        'expiryDates': data['option_data'][0]['oi_data']['records']['expiryDates']
    }


def get_nifty_chart_data(expiry_date):

    data = fetch_oi()

    nifty_cmps = [item['nifty_cmp'] for item in data['option_data']]
    timestamps = [item['timestamp'] for item in data['option_data']]

    ce_changes = []
    pe_changes = []
    pcrs = []

    for item in data['option_data']:
        oi_data = item['oi_data']['records']['data']

        ce_oi = sum([oi['CE']['openInterest'] for oi in oi_data if 'CE' in oi and oi['expiryDate']==expiry_date])
        pe_oi = sum([oi['PE']['openInterest'] for oi in oi_data if 'PE' in oi and oi['expiryDate']==expiry_date])
        pcrs.append(round(pe_oi/ce_oi, 2))

        ce_change = sum([oi['CE']['changeinOpenInterest'] for oi in oi_data if 'CE' in oi and oi['expiryDate']==expiry_date])
        pe_change = sum([oi['PE']['changeinOpenInterest'] for oi in oi_data if 'PE' in oi and oi['expiryDate']==expiry_date])
        ce_changes.append(ce_change)
        pe_changes.append(pe_change)

    return {
        'timestamps': timestamps,
        'nifty_cmps': nifty_cmps,
        'ce_changes': ce_changes,
        'pe_changes': pe_changes,
        'pcrs': pcrs
    }


def get_oi_chart_data(expiry_date):

    data = fetch_oi()

    expiry_data = [
        d for d in data['option_data'][-1]['oi_data']['records']['data'] 
        if d['expiryDate']==expiry_date
    ]

    return {
        'expiry_date': expiry_date,
        'data': expiry_data
    }


def get_strike_chart_data(strike, expiry_date):

    data = fetch_oi()

    timestamps = []
    ce_changes = []
    pe_changes = []
    ce_ltp = []
    pe_ltp = []

    for item in data['option_data']:
        timestamps.append(item['timestamp'])

        strike_data = [i for i in item['oi_data']['records']['data'] if i['strikePrice'] == int(strike) and i['expiryDate']==expiry_date]
        
        ce_changes.append(strike_data[0]['CE']['changeinOpenInterest'])
        pe_changes.append(strike_data[0]['PE']['changeinOpenInterest'])
        ce_ltp.append(strike_data[0]['CE']['lastPrice'])
        pe_ltp.append(strike_data[0]['PE']['lastPrice'])

    return {
        'timestamps': timestamps,
        'ce_changes': ce_changes,
        'pe_changes': pe_changes,
        'ce_ltp': ce_ltp,
        'pe_ltp': pe_ltp
    }