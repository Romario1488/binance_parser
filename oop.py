import requests
import json

class Binance:
    def showOrder(self):
        parsed_orders = self.__getOrders()
        parsed_sellers_rating = self.__getSellerRating(parsed_orders)
        summary = self.__getSellerStat(parsed_sellers_rating)
        with open('orders.txt', 'w', encoding='utf-8') as w_orders:
            w_orders.write(json.dumps(summary))

    def parseOrders(self, response):
        all_orders = {}
        for order in response['data']:

            if order['advertiser']['monthFinishRate'] >= 0.3:
                price = order['adv']['price']
                id = order['advertiser']['userNo']
                all_orders[id] = {"method": order['adv']['tradeMethods'][0]['tradeMethodName'],
                                  'rate': str(price) + ' ' + order['adv']['fiatUnit'],
                                  'nickName': order['advertiser']['nickName'],
                                  'seller_link': f"https://p2p.binance.com/ru/advertiserDetail?advertiserNo={id}"}
        return all_orders

    def __getSellerRating(self, all_orders):
        for seller_id in all_orders:
            r = requests.post(f"https://p2p.binance.com/bapi/c2c/v1/friendly/c2c/review/user-review-statistics",
                              json={"userNo": seller_id},
                              headers={'User-agent': 'your bot 0.1'})
            response_dealler_rating = r.json()
            self.__sellerRatingParse(response_dealler_rating, seller_id, all_orders)
        return all_orders

    def __sellerRatingParse(self, response_dealler_stat, seller_id, all_orders):
        all_orders[seller_id].update({"negativeCount": response_dealler_stat['data']['negativeCount'],
                                      "positiveCount: ": response_dealler_stat['data']['positiveCount']})
        return

    def __getSellerStat(self, all_orders):
        for seller_id in all_orders:
            r = requests.get(
                f"https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/user/profile-and-ads-list?userNo={seller_id}",
                headers={'User-agent': 'your bot 0.1'})

            response_dealler_stat = r.json()
            self.__sellerStatParse(response_dealler_stat, seller_id, all_orders)
        return all_orders

    def __sellerStatParse(self, response_dealler_stat, seller_id, all_orders):
        all_orders[seller_id].update({
            "avgTransferTime": int(response_dealler_stat['data']['userDetailVo']['userStatsRet'][
                                       'avgReleaseTimeOfLatest30day']),
            "registerDays: ": response_dealler_stat['data']['userDetailVo']['userStatsRet']['registerDays']})
        return

    def __getOrders(self):
        r = requests.post('https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search',
                          json={"page": 1, "rows": 20, "publisherType": "merchant",
                                "asset": "USDT", "tradeType": "BUY", "fiat": 'RUB'},
                          headers={'User-agent': 'your bot 0.1'})
        response = r.json()
        parsed_orders = self.parseOrders(response)
        return parsed_orders


if __name__ == '__main__':
    b = Binance()
    b.showOrder()
