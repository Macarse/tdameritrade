from tdameritrade import TDClient
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
    print('strangle_finder: ', symbol, date)


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
