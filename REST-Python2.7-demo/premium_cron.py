# coding:utf-8
import HuobiDMUtil
import time
import json

DIGITAL_CURRENCY_LIST = ['BTC', 'ETH', 'EOS', 'BCH', 'LTC', 'XRP', 'TRX']
TIME_PERIOD_LIST = ['_CW', '_NW', '_CQ']

WEBSITE = 'https://api.hbdm.com/'
API_MARKET_DETAIL_MERGED = 'market/detail/merged'
API_CONTRACT_INDEX = 'api/v1/contract_index'

DING_TALK = 'https://oapi.dingtalk.com/robot/send?' \
             'access_token=5a304120576fde895401d9e0024793bd04adea5f1cd79e8ca24cab5d654afdb7'

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


DING_DING_MARKDOWN_TEMPLATE = {
    "msgtype": "markdown",
    "markdown": {
        "title": "数字币--火币--溢价",
        "text": "### 数字币--火币--溢价    \n"
                "> 1. | 币\t| 指数 \t|           \n"
                "> 2. |---\t|---\t|               \n"
                "> 3. |BTC\t|10000.0\t|           \n"
    },
    "at": {
        "isAtAll": True
    }
}


if __name__ == '__main__':
    table_title = ["数字币",
                   "当周(溢价)", "次周(溢价)", "季度(溢价)",
                   "当周/季度(价差)", "次周/季度(价差)", "当周/次周(价差)"]

    table_data = []
    for dc in DIGITAL_CURRENCY_LIST:
        table_line = [dc]

        response = http_request_multi(WEBSITE + API_CONTRACT_INDEX, {'symbol': dc})
        dc_index = get_value_from_data(response, 'data', 'index_price')
        dc_index_ts = get_value_from_data(response, 'ts')

        #table_line.append(str(dc_index))

        tmp_map = {}
        for tp in TIME_PERIOD_LIST:
            response = http_request_multi(WEBSITE + API_MARKET_DETAIL_MERGED, {'symbol': dc + tp})
            close_price = get_value_from_data(response, 'tick', 'close')
            ts = get_value_from_data(response, 'ts')

            close_price = float(close_price) if close_price else None
            tmp_map[tp] = close_price

            table_line.append('%.2f‰' % (1000.0*(close_price-dc_index)/dc_index) if close_price and dc_index else None)

        CW = tmp_map[TIME_PERIOD_LIST[0]]
        NW = tmp_map[TIME_PERIOD_LIST[1]]
        CQ = tmp_map[TIME_PERIOD_LIST[2]]

        CW_CQ = '%.2f‰' % (1000.0 * (CQ - CW) / CW) if CW and CQ else None
        NW_CQ = '%.2f‰' % (1000.0 * (CQ - NW) / NW) if NW and CQ else None
        CW_NW = '%.2f‰' % (1000.0 * (NW - CW) / CW) if CW and NW else None

        table_line.append(CW_CQ)
        table_line.append(NW_CQ)
        table_line.append(CW_NW)

        '''
                       timeout = ts - dc_index_ts
            if timeout > MAX_RESPONSE_TIMEOUT:
                line += '(%.2f)' % (timeout / 1000.0)
            line = u'[%.2f‰]' % (1000.0 * (float(close_price) - dc_index) / dc_index)
        '''
        table_data.append(table_line)

    send_data = '* ' + ", ".join(table_title) + '\n'
    for line in table_data:
        send_data += '* ' + ", ".join(line) + '\n'

    DING_DING_MARKDOWN_TEMPLATE['markdown']['text'] = send_data
    HuobiDMUtil.http_post_request(DING_TALK, params=DING_DING_MARKDOWN_TEMPLATE)

