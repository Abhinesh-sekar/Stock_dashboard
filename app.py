import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

@st.cache_data
def load_data():
    components = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    if 'SEC filings' in components.columns:
        components = components.drop('SEC filings', axis=1)
    return components.set_index('Symbol')

@st.cache_data
def load_quotes(asset, start_date, end_date):
    data = yf.download(asset, start=start_date, end=end_date)
    if 'Adj Close' not in data.columns:
        st.write("Available columns in downloaded data:", data.columns)
        st.error("'Adj Close' column is missing in the downloaded data. Please check the stock ticker or try a different one.")
        return None
    return data

def main():
    components = load_data()
    title = st.empty()
    st.sidebar.title("Options")

    def label(symbol):
        a = components.loc[symbol]
        return symbol + ' - ' + a.Security

   

    st.sidebar.subheader('Select asset')
    asset = st.sidebar.selectbox('Click below to select a new asset',
                                 components.index.sort_values(), index=3,
                                 format_func=label)
    title.title(components.loc[asset].Security)

    if st.sidebar.checkbox('View company info', True):
        st.table(components.loc[asset])

   
    st.sidebar.subheader('Select Date Range')
    start_date = st.sidebar.date_input('Start date', value=pd.to_datetime('2020-01-01'))
    end_date = st.sidebar.date_input('End date', value=pd.to_datetime('today'))

    
    if start_date > end_date:
        st.error('Start date must be before end date.')
        return

    data0 = load_quotes(asset, start_date, end_date)
    if data0 is None:
        st.stop()  

    data = data0.dropna()
    data.index.name = None

    data2 = data[['Adj Close']].copy()
    data2 = data2.reset_index()
    data2.columns = ['Date', 'Adj Close']

    sma = st.sidebar.checkbox('Simple Moving Average (SMA)')
    if sma:
        period = st.sidebar.slider('SMA period', min_value=5, max_value=500, value=20, step=1)
        data['SMA'] = data['Adj Close'].rolling(period).mean()
        data2['SMA'] = data['SMA'].values  # Add SMA to data2 for plotting

    # Create Plotly figure for better customization
    fig = go.Figure()

    # Plot Adj Close
    fig.add_trace(go.Scatter(x=data2['Date'], y=data2['Adj Close'], mode='lines', name='Adj Close', line=dict(color='blue')))

    # Plot SMA with custom color if checked
    if sma:
        fig.add_trace(go.Scatter(x=data2['Date'], y=data2['SMA'], mode='lines', name=f'SMA {period}', line=dict(color='red')))

    # Update layout for better visuals
    fig.update_layout(title=f'{asset} Price and SMA',
                      xaxis_title='Date',
                      yaxis_title='Price',
                      template='plotly_dark')

    st.subheader('Chart')
    st.plotly_chart(fig)  # Display Plotly chart

    if st.sidebar.checkbox('View statistics'):
        st.subheader('Statistics')
        st.table(data2[['Adj Close']].describe())

    if st.sidebar.checkbox('View quotes'):
        st.subheader(f'{asset} historical data')
        st.write(data2)

if __name__ == '__main__':
    main()
