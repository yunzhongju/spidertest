from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import requests
import time
import execjs
# 百度指数
# 	爬取源：关键字搜索    易烊千玺
# 	需求字段：最近30天的搜索指数的数值
js = '''function decrypt(t, e) {
            for (var n = t.split(""), i = e.split(""), a = {}, r = [], o = 0; o < n.length / 2; o++) a[n[o]] = n[n.length / 2 + o];
            for (var s = 0; s < e.length; s++) r.push(a[i[s]]);
            return r.join("")
        }'''

headers = {
    'cookie': 'BIDUPSID=8B91236F6EFEA317BF0B0C163186148B; PSTM=1575865457; BAIDUID=8B91236F6EFEA3173A1EA568BA982A63:FG=1; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; delPer=0; H_PS_PSSID=1432_21105_30211; PSINO=1; BDSFRCVID=4hPsJeCCxG3JggRwPBEGtN_2wAFOeQZRddMu3J; H_BDCLCKID_SF=tR30WJbHMTrDHJTg5DTjhPrMjM7TbMT-027OKKOF5b3CfUJtQfJMXlRX5PQlW-QIyHrb0p6athF0HPonHj-5D5oW3J; Hm_lvt_d101ea4d2a5c67dab98251f0b5de24dc=1575970073,1575970169,1576035558,1576058343; BDUSS=VQfnpkVUJzUnQtSFJ1UjlIbHRLaFVselM3NWRQSlRtYS1uOVZWZHpvfmtTeGhlRVFBQUFBJCQAAAAAAAAAAAEAAABvFk9huN-3wNP5us23qLn6AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOS-8F3kvvBdT1; CHKFORREG=b8252d38749c9710a2b998d0a002cabb; bdindexid=jk5df0olcpr6h7hgc3qgickt53; Hm_lpvt_d101ea4d2a5c67dab98251f0b5de24dc=1576058612',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}
data_url = 'https://index.baidu.com/api/SearchApi/index?word={}&area=0&days=30'
uniqid_url = 'https://index.baidu.com/Interface/ptbk?uniqid={}'
keys = ["all", "pc", "wise"]


class BaiDuIndex(object):

    def __init__(self):
        self.js_handler = self.get_js_handler()
        self.session = self.get_session()

    def decrypt(self, key, data):
        return self.js_handler.call('decrypt', key, data)

    def do_request(self, url):
        return self.session.get(url)

    def parse(self, response, uniqid):
        result = []
        data_dict = response.get("data").get("userIndexes")[0]
        for key in keys:
            result.append({key: self.decrypt(uniqid, data_dict.get(key).get("data"))})
        return result

    def get_baidu_index(self, keyword):
        response = self.do_request(data_url.format(keyword)).json()
        uniqid = self.do_request(uniqid_url.format(response.get("data").get("uniqid"))).json().get("data")
        return self.parse(response, uniqid)

    @staticmethod
    def get_js_handler():
        return execjs.compile(js)

    @staticmethod
    def get_session():
        session = requests.session()
        session.headers = headers
        session.verify = False
        return session


if __name__ == '__main__':
    baidu = BaiDuIndex()
    print(baidu.get_baidu_index("易烊千玺"))
