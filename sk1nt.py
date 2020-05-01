from tdameritrade import TDClient
import pandas as pd
import argparse

def main():
    parser = argparse.ArgumentParser(description='Options on Options')
    subparsers = parser.add_subparsers(dest='subparser')

    strangle_check_parser = subparsers.add_parser('strangle_check')
    strangle_check_parser.add_argument('--first', '-f', required=True, help='First leg with fmt {TICKER}_{YYYY-MM-DD}_{CALL/PUT}_{STRIKE}')
    strangle_check_parser.add_argument('--second', '-s', required=True, help='First leg with fmt {TICKER}_{YYYY-MM-DD}_{CALL/PUT}_{STRIKE}')

    strangle_finder_parser = subparsers.add_parser('strangle_finder')
    strangle_finder_parser.add_argument('--date', '-d', required=True, help='Date in YYYY-MM-DD')
    strangle_finder_parser.add_argument('--symbol', '-s', required=True, help='Symbol like SPY')

    kwargs = vars(parser.parse_args())
    globals()[kwargs.pop('subparser')](**kwargs)

def strangle_check(first, second):
    leg1 = parse_leg(first)
    leg2 = parse_leg(second)
    tdclient = TDClient()

    call = tdclient.optionsDF(symbol=leg1['symbol'], contractType=leg1['contractType'], strike=leg1['strike'], fromDate=leg1['date'], toDate=leg1['date'])
    put = tdclient.optionsDF(symbol=leg2['symbol'], contractType=leg2['contractType'], strike=leg2['strike'], fromDate=leg2['date'], toDate=leg2['date'])

    print("Your call's delta is %s and your put delta is %s" %(call.delta[0], put.delta[0]))
    diff = abs(call.delta[0]) - abs(put.delta[0])
    if diff <= 0.01:
        print("This looks like a good trade with delta diff %s", str(diff))
    else:
        print("Don't do that trade :(")


def strangle_finder(symbol, date):
    tdclient = TDClient()
    df = tdclient.optionsDF(symbol=symbol, fromDate=date, toDate=date)

    interest_filter = df["openInterest"]+df["totalVolume"] > 0
    delta_16_filter = abs(abs(df['delta'])-0.16) < 0.01
    filtered = df[['putCall', 'description', 'delta', 'strikePrice', 'bid', 'ask']].where(delta_16_filter).dropna()

    calls_df = filtered[filtered['putCall']=='CALL']
    puts_df = filtered[filtered['putCall']=='PUT']

    # If we don't have at least 1 call or 1 put, return
    if len(calls_df.index) == 0 or len(puts_df.index) == 0:
        print("Couldn't find any good strangles. Sorry")
        return

    # Small hack to cross join
    pd.options.mode.chained_assignment = None
    calls_df['merge_key'] = 0
    puts_df['merge_key'] = 0
    trades = calls_df.merge(puts_df, on='merge_key', suffixes=('_call', '_put'))

    # Additional columns to better analize data
    trades['max_profit'] = round(trades['bid_call']+trades['bid_put'], 2)
    trades['strategy_delta'] = abs(trades['delta_call'])+abs(trades['delta_put'])

    # print max profit
    max_profit = trades.sort_values('max_profit', ascending=False).iloc[0]
    print("Max Profit: %s/%s @%s with delta %s" %(max_profit['strikePrice_call'], max_profit['strikePrice_put'], max_profit['max_profit'], max_profit['strategy_delta']))

    # higher probability
    prob = trades.sort_values('strategy_delta').iloc[0]
    print("Best probability: %s/%s @%s with delta %s" %(prob['strikePrice_call'], prob['strikePrice_put'], prob['max_profit'], prob['strategy_delta']))

    # Best downside protection
    downside = trades.sort_values('strikePrice_put', ascending=False).iloc[0]
    print("Best downside risk: %s/%s @%s with delta %s" %(downside['strikePrice_call'], downside['strikePrice_put'], downside['max_profit'], downside['strategy_delta']))




def parse_leg(text):
    ret = {}
    splits = text.split('_')
    ret['symbol'] = splits[0]
    ret['date'] = splits[1]
    ret['contractType'] = splits[2]
    ret['strike'] = splits[3]
    return ret

if __name__ == '__main__':
    main()
