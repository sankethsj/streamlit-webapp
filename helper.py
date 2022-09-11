import pandas as pd

def color_negative_red(value):
    if "(" in str(value):
        value = float(value.split("(")[-1].split(")")[0])
    
    if "%" in str(value):
        value = float(value.replace('%',''))

    if value < 0:
        color = 'red'
    elif value > 0:
        color = 'green'
    else:
        color = 'black'

    return 'color: %s' % color

def atm_strike_row_style(row, atm_strike):
    if row['Strike Price'] == atm_strike:
        return pd.Series('background-color: #262626;', row.index)
    else:
        return pd.Series('', row.index)

def oi_interpret(x, script:str):

    if x[f'{script}.change'] > 0 and x[f'{script}.changeinOpenInterest'] > 0:
        return "Long Buildup"

    elif x[f'{script}.change'] < 0 and x[f'{script}.changeinOpenInterest'] > 0:
        return "Short Buildup"

    elif x[f'{script}.change'] > 0 and x[f'{script}.changeinOpenInterest'] < 0:
        return "Short Covering"
    
    elif x[f'{script}.change'] < 0 and x[f'{script}.changeinOpenInterest'] < 0:
        return "Long Covering"
    
    else:
        return "Unknown"

def bg_color_negative_red(value):

    if str(value) in ["Long Buildup", "Short Covering"]:
        value = 1
    elif str(value) in ["Long Covering", "Short Buildup"]:
        value = -1
    else:
        value = 0
    
    if value < 0:
        color = 'red'
    elif value > 0:
        color = 'green'
    else:
        color = 'black'
    
    return 'background-color: %s' % color
