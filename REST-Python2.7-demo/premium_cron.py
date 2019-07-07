# coding:utf-8
import HuobiDMUtil
import datetime
import time
import json
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

DIGITAL_CURRENCY_LIST = ['BTC', 'ETH', 'EOS', 'BCH', 'LTC', 'XRP', 'TRX']
TIME_PERIOD_LIST = ['_CW', '_NW', '_CQ']

WEBSITE = 'https://api.hbdm.com/'
API_MARKET_DETAIL_MERGED = 'market/detail/merged'
API_CONTRACT_INDEX = 'api/v1/contract_index'

DING_TALK = 'https://oapi.dingtalk.com/robot/send?' \
             'access_token=16a17282c10461487893900a474342778355f0ee1154fd290b29ac53ea349692'

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
    monitor_period = 5
    send_flag = False
    with open('config/alarm.yml', 'r') as stream:
        monitor = yaml.load(stream, Loader=Loader)

    print 'BTC' in monitor['MONITOR']
    exit(0)

    table_title = ["当/季", "次/季", "当/次", "当", "次", "季"]

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

            table_line.append('%.1f' % (1000.0*(close_price-dc_index)/dc_index) if close_price and dc_index else None)

        CW = tmp_map[TIME_PERIOD_LIST[0]]
        NW = tmp_map[TIME_PERIOD_LIST[1]]
        CQ = tmp_map[TIME_PERIOD_LIST[2]]

        CW_CQ = '%.1f' % (1000.0 * (CQ - CW) / CW) if CW and CQ else None
        NW_CQ = '%.1f' % (1000.0 * (CQ - NW) / NW) if NW and CQ else None
        CW_NW = '%.1f' % (1000.0 * (NW - CW) / CW) if CW and NW else None

        table_line.insert(1, CW_NW)
        table_line.insert(1, NW_CQ)
        table_line.insert(1, CW_CQ)

        '''
                       timeout = ts - dc_index_ts
            if timeout > MAX_RESPONSE_TIMEOUT:
                line += '(%.2f)' % (timeout / 1000.0)
            line = u'[%.2f‰]' % (1000.0 * (float(close_price) - dc_index) / dc_index)
        '''
        table_data.append(table_line)

    send_data = ""
    send_data += "## " + ", ".join(table_title) + '\n'
    for line in table_data:
        send_data += '* ' + ", ".join(line) + '\n'
        threshold = monitor['MONITOR'][line[0]]['threshold'] \
            if line[0] in monitor['MONITOR'] \
            else monitor['MONITOR']['DEFAULT']['threshold']

        if float(line[1]) > threshold + monitor_period \
                or float(line[1]) < threshold - monitor_period:
            send_flag = True
            monitor['MONITOR'][line[0]]['threshold'] = float(line[1]) - float(line[1]) % monitor_period

    from datetime import datetime
    import pytz
    cn_dt = datetime.now(tz=pytz.timezone('Asia/Shanghai'))

    send_data += "\n\n### " + cn_dt.strftime('%Y-%m-%d %H:%M:%S')

    DING_DING_MARKDOWN_TEMPLATE['markdown']['text'] = send_data
    if send_flag:
        HuobiDMUtil.http_post_request(DING_TALK, params=DING_DING_MARKDOWN_TEMPLATE)
        with open('config/alarm.yml', 'w') as write:
            write.write(monitor)

