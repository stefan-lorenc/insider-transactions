import yfinance as yf
import pandas as pd
import numpy as np
import sys
import warnings
from pandas.tseries.holiday import AbstractHolidayCalendar, Holiday, nearest_workday, \
    USMartinLutherKingJr, USPresidentsDay, GoodFriday, USMemorialDay, \
    USLaborDay, USThanksgivingDay
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from sklearn import preprocessing
from sklearn.metrics import f1_score

spy_hist = yf.Ticker('^GSPC').history(period='max')
vix_hist = yf.Ticker('^VIX').history(period='max')


class USTradingCalendar(AbstractHolidayCalendar):
    rules = [
        Holiday('NewYearsDay', month=1, day=1, observance=nearest_workday),
        USMartinLutherKingJr,
        USPresidentsDay,
        GoodFriday,
        USMemorialDay,
        Holiday('Juneteenth', month=6, day=20, observance=nearest_workday),
        Holiday('USIndependenceDay', month=7, day=4, observance=nearest_workday),
        USLaborDay,
        USThanksgivingDay,
        Holiday('Christmas', month=12, day=25, observance=nearest_workday)
    ]


def nearest(items, pivot):
    try:
        near = max([i for i in items if i < pivot])
        return near
    except ValueError as e:
        print(e)


def sector_application(tick):
    try:
        value = yf.Ticker(tick).info['sector']
        return value
    except KeyError as e:
        return None


def security_performance(ticker_info):
    try:
        hist = yf.Ticker(ticker_info[0]).history(period='max', debug=False)
        month_performance = (hist.loc[ticker_info[1]]['Close'] - hist.loc[ticker_info[2]]['Open']) / \
                            hist.loc[ticker_info[2]]['Open']

        two_week_performance = (hist.loc[ticker_info[1]]['Close'] - hist.loc[ticker_info[3]]['Open']) / \
                               hist.loc[ticker_info[3]]['Open']

        classification = hist[ticker_info[1]:ticker_info[4]]

        classification['Midpoint'] = ((classification['High'] + classification['Low']) / 2)
        classification['rows'] = range(0, len(classification.axes[0]))
        mid = classification['Midpoint'].tolist()
        open = classification['Open'].tolist()

        exit_mid = np.quantile(mid, 0.75)
        exit_open = np.quantile(open, 0.75)

        ret_mid_exit = (exit_mid - hist.loc[ticker_info[1]]['Open']) / hist.loc[ticker_info[1]]['Open']
        ret_open_exit = (exit_open - hist.loc[ticker_info[1]]['Open']) / hist.loc[ticker_info[1]]['Open']
        days_to_mid_exit = classification['rows'][classification.Midpoint.eq(exit_mid).idxmax()]
        days_to_open_exit = classification['rows'][classification.Open.eq(exit_open).idxmax()]

        return [month_performance, two_week_performance, ret_mid_exit, ret_open_exit, days_to_mid_exit,
                days_to_open_exit]
    except Exception as e:
        return [None, None, None, None, None, None]


def market_performance(date_info):
    global spy_hist
    global vix_hist

    try:
        spy_month_performance = (spy_hist.loc[date_info[0]]['Close'] - spy_hist.loc[date_info[1]]['Open']) / \
                                spy_hist.loc[date_info[1]]['Open']

        spy_two_week_performance = (spy_hist.loc[date_info[0]]['Close'] - spy_hist.loc[date_info[2]]['Open']) / \
                                   spy_hist.loc[date_info[2]]['Open']

        vix_month_change = (vix_hist.loc[date_info[0]]['Close'] - vix_hist.loc[date_info[2]]['Open']) / \
                           vix_hist.loc[date_info[2]]['Open']

        vix_two_week_change = (vix_hist.loc[date_info[0]]['Close'] - vix_hist.loc[date_info[2]]['Open']) / \
                              vix_hist.loc[date_info[2]]['Open']

        return [spy_month_performance, spy_two_week_performance, vix_month_change, vix_two_week_change]
    except Exception as e:
        return [None, None, None, None]

    pass


def earnings_lead_lag(earn_info):
    try:
        # time.sleep(1.8)
        dated = yf.Ticker(earn_info[0]).earnings_dates.index.values
        near_lead = nearest(dated, earn_info[1])
        leading_days = (earn_info[1] - near_lead).astype('timedelta64[D]').astype(int)
        return leading_days
    except Exception as e:
        print(e)
        return None


def main():
    pd.set_option("expand_frame_repr", False)
    warnings.filterwarnings("ignore")  # disable this if there are some problems you can't see... idiot
    purchases = pd.read_csv('purchase_v3.csv')
    purchases['Ticker'] = purchases['Ticker'].astype(str)
    purchases['Filing Date'] = pd.to_datetime(purchases['Filing Date'], format='%Y-%m-%d')
    purchases['Trade Date'] = pd.to_datetime(purchases['Trade Date'], format='%Y-%m-%d')
    purchases['Action Date'] = pd.to_datetime(purchases['Action Date'], format='%Y-%m-%d')
    purchases['filing_check_month'] = pd.to_datetime(purchases['filing_check_month'], format='%Y-%m-%d')
    purchases['Trade Day of Week'] = purchases['Trade Date'].dt.dayofweek
    purchases['Filing Day of Week'] = purchases['Filing Date'].dt.dayofweek
    purchases = purchases.drop('2-Week Performance Following Transaction', axis=1)
    purchases = purchases.drop('Closing Price on Filing Date', axis=1)
    purchases = purchases.drop('One Month Performance Following Transaction', axis=1)

    with ThreadPoolExecutor(max_workers=12) as executor:
        tickers = purchases['Ticker'].values
        purchases['Sector'] = list(
            tqdm(executor.map(sector_application, tickers), total=len(tickers), desc=' Sector Collection',
                 unit='Sectors'))
        executor.shutdown(wait=True)

    with ThreadPoolExecutor(max_workers=12) as executor:
        ticker_info = [[w, x, y, z, a] for w, x, y, z, a in
                       zip(purchases['Ticker'].values, purchases['Action Date'].values,
                           purchases['performance_check_month'].values,
                           purchases['performance_check_2_weeks'].values,
                           purchases['classification_check_month'].values)]
        ticker_hist_info = list(
            tqdm(executor.map(security_performance, ticker_info), total=len(ticker_info), desc=' Historical Collection',
                 unit='Pricing Info'))
        purchases['One Month Prior Performance'] = [info[0] for info in ticker_hist_info]
        purchases['2-Week Prior Performance'] = [info[1] for info in ticker_hist_info]
        purchases['Return if exited at the 75th percentile midpoint of daily price action'] = [info[2] for info in
                                                                                               ticker_hist_info]
        purchases['Return if exited at the 75th percentile open of daily price action'] = [info[3] for info in
                                                                                           ticker_hist_info]

        purchases['Days to midpoint exit'] = [info[4] for info in ticker_hist_info]
        purchases['Days to open exit'] = [info[5] for info in
                                          ticker_hist_info]  # will take the average exit time for the options

        executor.shutdown(wait=True)

    with ThreadPoolExecutor(max_workers=12) as executor:
        market_info = [[x, y, z] for x, y, z in zip(purchases['Action Date'].values,
                                                    purchases['performance_check_month'].values,
                                                    purchases['performance_check_2_weeks'].values)]
        market_hist_info = list(
            tqdm(executor.map(market_performance, market_info), total=len(market_info), desc=' Market Collection',
                 unit='Market Info'))

        purchases['One Month Prior Market Performance'] = [info[0] for info in market_hist_info]
        purchases['2-Week Prior Index Performance'] = [info[1] for info in market_hist_info]
        purchases['One Month Prior Volatility Change'] = [info[2] for info in market_hist_info]
        purchases['2-Week Prior Volatility Change'] = [info[3] for info in market_hist_info]
        executor.shutdown(wait=True)

    def transaction_history(transact):
        temp = purchases.groupby('Ticker')
        filing_dates_for_sim = temp.get_group(transact[0])['Filing Date'].tolist()
        indexes_for_sim = temp.get_group(transact[0]).index.tolist()

        sim_trans = []

        for i, j in zip(indexes_for_sim, filing_dates_for_sim):
            if transact[3] <= j <= transact[2] and i != transact[1]:
                sim_trans.append(i)

        if len(sim_trans) != 0:
            transactions = purchases.iloc[sim_trans]
            num_of_transactions = len(transactions)
            days_since_most_recent_transaction = (transact[2] - transactions.iloc[0]['Filing Date']).days
            return [num_of_transactions, days_since_most_recent_transaction]
        else:
            return [0, -1]

    with ThreadPoolExecutor(max_workers=12) as executor:
        transact_ticks = [[w, x, y, z] for w, x, y, z in
                          zip(purchases['Ticker'].values, purchases.index.values, purchases['Filing Date'].values,
                              purchases['filing_check_month'].values)]
        transaction_hist_info = list(
            tqdm(executor.map(transaction_history, transact_ticks), total=len(transact_ticks),
                 desc=' Historical Transactions',
                 unit=' Transactions Evaluated'))

        purchases['Number of Recent Transactions'] = [info[0] for info in transaction_hist_info]
        purchases['Days Since Last Recent Transaction'] = [info[1] for info in transaction_hist_info]

        executor.shutdown(wait=True)

    print(purchases.head())

    purchases.to_csv('purchase_svm_rf_v0.0.2.csv', index=False)


if __name__ == '__main__':
    # main()
    print(yf.Ticker('AAPL').info)


    pd.set_option("expand_frame_repr", False)
    cols = ['Difference btw. filing and trade date', 'Value', 'Delta Own Conv.',
            'Sector', 'One Month Prior Performance', '2-Week Prior Performance',
            'One Month Prior Market Performance', '2-Week Prior Index Performance',
            'One Month Prior Volatility Change', '2-Week Prior Volatility Change',
            'Return if exited at the 75th percentile midpoint of daily price action',
            'Return if exited at the 75th percentile open of daily price action']
    # , 'Days to midpoint exit',
    #     'Days to open exit']

    purchases = pd.read_csv('purchase_svm_rf_v0.0.2.csv', usecols=cols)

    le = preprocessing.LabelEncoder()
    purchases['Sector'] = le.fit_transform(purchases['Sector'])
    purchases['Class'] = -1
    purchases.loc[purchases['Return if exited at the 75th percentile open of daily price action'] >= 0.07, 'Class'] = 1
    purchases.loc[purchases['Return if exited at the 75th percentile open of daily price action'] < 0.07, 'Class'] = 0

    purchases = purchases.dropna()
    print(purchases.sample(15))

    print(purchases['Class'].value_counts() / (len(purchases)))

    x = purchases.drop(['Class', 'Return if exited at the 75th percentile open of daily price action',
                        'Return if exited at the 75th percentile midpoint of daily price action'], axis=1)
    y = purchases['Class']
