import requests



class Binance:
    def showOrder(self):
        orders_info, dealler_id = self.__getOrders()
        result = self.__getUserStat(orders_info, dealler_id)
        with open('Orders.txt', 'a', encoding='utf-8') as orders:
            for el in result:
                print(el)
                orders.write('\n'.join(el)+'\n\n')

    def parseOrders(self):
        r = requests.post('https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search',
                          json={"page": 1, "rows": 20, "publisherType": "merchant",
                                "asset": "USDT", "tradeType": "BUY", "fiat": 'RUB'},
                          headers={'User-agent': 'your bot 0.1'})
        response = r.json()
        return response

    def __getOrders(self):
        get_methods = self.parseOrders()
        trade_methods_name = []
        dealler_id = []
        orders = []
        rate = []
        for order in get_methods['data']:
            if order['advertiser']['monthFinishRate'] == 1.0:
                dealler_id.append(order['advertiser']['userNo'])
                trade_methods_name.append(order['adv']['tradeMethods'][0]['tradeMethodName'])
                price = order['adv']['price']
                rate.append(str(price) + ' ' + order['adv']['fiatUnit'])
        i = 0

        deallers = []
        for id in dealler_id:
            r = requests.get(f"https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/user/profile-and-ads-list?userNo={id}",
                             headers={'User-agent': 'your bot 0.1'})
            response = r.json()
            deallers.append(response)

        i = 0
        for order in deallers:
            current_order = [
                "method: " + trade_methods_name[i],
                'rate: ' + rate[i],
                "nickName: " + order['data']['userDetailVo']['nickName'],
                "link: " + 'https://p2p.binance.com/ru/advertiserDetail?advertiserNo=' + order['data']['userDetailVo'][
                    'userNo']]
            i += 1
            orders.append(current_order)
        return orders, dealler_id

    def __getUserStat(self, orders, dealler_id):
        dealler_info = []
        for id in dealler_id:
            r = requests.get(f"https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/user/profile-and-ads-list?userNo={id}",
                             headers={'User-agent': 'your bot 0.1'})
            response = r.json()
            dealler_info.append(response)

        i = 0
        for order in orders:
            print(order)
            r = requests.post(f"https://p2p.binance.com/bapi/c2c/v1/friendly/c2c/review/user-review-statistics",
                              json={"userNo": dealler_id[i]},
                              headers={'User-agent': 'your bot 0.1'})
            response_dealler_stat = r.json()
            current_seller = [
                "negativeCount: " + str(response_dealler_stat['data']['negativeCount']),
                "positiveCount: " + str(response_dealler_stat['data']['positiveCount']),
                "avgTransferTime: " + str(int(
                    dealler_info[i]['data']['userDetailVo']['userStatsRet']['avgReleaseTimeOfLatest30day'])),
                "registerDays: " + str(dealler_info[i]['data']['userDetailVo']['userStatsRet']['registerDays'])]

            orders[i] += current_seller

            i += 1

        return orders


if __name__ == '__main__':
    b = Binance()
    b.showOrder()
