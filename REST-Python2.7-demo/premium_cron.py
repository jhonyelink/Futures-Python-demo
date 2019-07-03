# coding:utf-8
import HuobiDMUtil
import time
import json

DIGITAL_CURRENCY_LIST = ['BTC', 'ETH', 'EOS', 'BCH', 'LTC', 'XRP', 'TRX']
TIME_PERIOD_LIST = ['_CW', '_NW', '_CQ']

WEBSITE = 'https://api.hbdm.com/'
API_MARKET_DETAIL_MERGED = 'market/detail/merged'
API_CONTRACT_INDEX = 'api/v1/contract_index'

MAX_RESPONSE_TIMEOUT = 300


def get_value_from_data(response_data, global_key, *args):
    if response_data:
        if 'ok' == response.get('status'):
            result = response_data.get(global_key)
            if type(result) == dict:
                pass
            elif type(result) == list and len(result) > 0:
                result = result[0]
            else:
                return result

            for arg in args:
                if result:
                    result = result.get(arg)
                else:
                    return

            return result

    return


def http_request_multi(api, args, times=3):
    for i in xrange(times):
        response = HuobiDMUtil.http_get_request(api, params=args)
        if response:
            return response


if __name__ == '__main__':
    for dc in DIGITAL_CURRENCY_LIST:
        line = dc

        response = http_request_multi(WEBSITE + API_CONTRACT_INDEX, {'symbol': dc})
        dc_index = get_value_from_data(response, 'data', 'index_price')
        dc_index_ts = get_value_from_data(response, 'ts')

        line += '\t' + str(dc_index)

        for tp in TIME_PERIOD_LIST:
            response = http_request_multi(WEBSITE + API_MARKET_DETAIL_MERGED, {'symbol': dc + tp})
            close_price = get_value_from_data(response, 'tick', 'close')
            ts = get_value_from_data(response, 'ts')

            line += '\t' + str(close_price)
            line += u'[%.2f‰]' % (1000.0 * (float(close_price) - dc_index) / dc_index)
            timeout = ts - dc_index_ts
            if timeout > MAX_RESPONSE_TIMEOUT:
                line += '(%.2f)' % (timeout / 1000.0)

        print line

