import pandas as pd
import streamlit as st

from helper import *
from option_chain import fetch_oi

st.set_page_config(layout="wide")
st.title('OI Analytics')



# Using object notation
index_selected = st.sidebar.selectbox(
    "Select Index :",
    ("NIFTY",)
)

data = fetch_oi(index_selected)

if data['status'] == 'ok':

	st.markdown(f"""
	### {index_selected} : {data['last']} ({round(data['variation'], 2)})
	Market Status : {data['marketStatus'].upper()}
	""")

	st.caption(f"Last updated at : {data['timestamp']}")


	df = pd.json_normalize(data['data'])

	df['CE Positions'] = df.apply(lambda x: oi_interpret(x, 'CE'), axis=1)
	df['PE Positions'] = df.apply(lambda x: oi_interpret(x, 'PE'), axis=1)

	df['CE.pchangeinOpenInterest'] = round(df['CE.pchangeinOpenInterest'], 2).astype(str) +"%"
	df['PE.pchangeinOpenInterest'] = round(df['PE.pchangeinOpenInterest'], 2).astype(str) +"%"
	df['CE.lastPrice'] = df['CE.lastPrice'].astype(str) +"("+ round(df['CE.pChange'], 2).astype(str) +")"
	df['PE.lastPrice'] = df['PE.lastPrice'].astype(str) +"("+ round(df['PE.pChange'], 2).astype(str) +")"

	required_columns = ['CE Positions','CE.openInterest', 'CE.changeinOpenInterest', 'CE.pchangeinOpenInterest', 'CE.lastPrice',
	'strikePrice', 'PE.lastPrice', 'PE.changeinOpenInterest', 'PE.pchangeinOpenInterest', 'PE.openInterest','PE Positions']
	df = df[required_columns]

	rename_columns = ['CE Positions', 'CE OpenInterest', 'CE ChangeinOI', '% CE ChangeinOI', 'CE LTP',
	'Strike Price', 'PE LTP', 'PE ChangeinOI', '% PE ChangeinOI', 'PE OpenInterest', 'PE Positions']
	df.columns = rename_columns

	# display OI-chart
	st.bar_chart(df, height=600, x="Strike Price", y=["CE ChangeinOI","PE ChangeinOI"], use_container_width=True)


	change_in_ce_oi = sum([d['CE']['changeinOpenInterest'] for d in data['data'] if 'CE' in d])
	change_in_pe_oi = sum([d['PE']['changeinOpenInterest'] for d in data['data'] if 'PE' in d])

	st.markdown(f"""
	***
	||Total Open Interest|Total Volume| Total Change in OI|
	|--|----|----|----|
	| CE | {data['CE']['totOI']} | {data['CE']['totVol']} | {change_in_ce_oi} |
	| PE | {data['PE']['totOI']} | {data['PE']['totVol']} | {change_in_pe_oi} |
	| Difference | {data['CE']['totOI']-data['PE']['totOI']}| {data['CE']['totVol']-data['PE']['totVol'] } | {change_in_ce_oi - change_in_pe_oi} |

	***
	""")


	df = df.style.applymap(color_negative_red, subset=[
			'CE ChangeinOI','PE ChangeinOI', 
			'% CE ChangeinOI', '% PE ChangeinOI',
			'CE LTP','PE LTP'
		]).applymap(bg_color_negative_red, subset=[
			'CE Positions','PE Positions'
		]).bar(subset=['CE OpenInterest'], color='#ff781c')

	df = df.apply(lambda x: atm_strike_row_style(x, data['atm_strike']), axis=1)

	st.subheader("Open Interest")
	st.text(f"Expiry date : {data['data'][0]['expiryDate']}")
	st.dataframe(df, width=1280, height=700)

else:

	st.json(data)

