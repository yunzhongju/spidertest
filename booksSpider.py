import time

import requests
import pymysql


class BooksSpider:

    def __init__(self):
        self.conn = conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='123456',
                                           database='books_db', charset='utf8')
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        self.url = "https://api-freesy.jinhuyu.cn/api/condition_query"
        self.categorie = []
        self.params = {
            "cat_id": '',
            "page": 1,
            "serial_status": "",
            "sex": 2,
            "sort": 1
        }
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36 MicroMessenger/7.0.4.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat",
            "Host": "api-freesy.jinhuyu.cn",
            "Connection": "keep-alive",
            "Referer": "https://servicewechat.com/wx5aa56d620688753e/10/page-frame.html",
            "content-type": "application/x-www-form-urlencoded",
            "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczpcL1wvYXBpLWZyZWVzeS5qaW5odXl1LmNuXC9hcGlcL2xvZ2luIiwiaWF0IjoxNTgzNTAwODcyLCJuYmYiOjE1ODM1MDA4NzIsImp0aSI6IkVuQ25UVFZWckkyQXRoTlMiLCJzdWIiOjEzNjQyNDIxLCJwcnYiOiIyM2JkNWM4OTQ5ZjYwMGFkYjM5ZTcwMWM0MDA4NzJkYjdhNTk3NmY3In0.1UgxmwWTkc0K8ceg10ZSlHeUhEUkeGTAM1vftH7lQAo"
        }

    def start(self):
        res = requests.get(self.url, params=self.params, headers=self.headers, verify=False).json()
        pages = res["pagination"]["total_pages"]
        for page in range(1, pages):
            self.params["page"] = page
            res = requests.get(self.url, params=self.params, headers=self.headers, verify=False).json()
            b_id = self.handle_books(res)
            time.sleep(3)
            self.handle_chapter(b_id)
        self.close()
        self.conn.close()

    def handle_books(self, res):
        books = res["data"]
        for book in books:
            id = book["id"]
            name = book["name"]
            print(name)
            desc = book["desc"]
            author = book["pen_name"]
            img = book["img"]
            serial_status = book["serial_status"]
            categorie = book["cat_name"]
            view_count, word_count = self.handle_book_detail(id)
            sex = self.params["sex"]
            data = [id, name, desc, author, img, serial_status, categorie, view_count, word_count, sex]
            sql = "insert into book values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            self.cursor.execute(sql, data)
            self.conn.commit()
            return id

    def handle_chapter(self, book_id):
        url = f"https://api-freesy.jinhuyu.cn/api/book/{book_id}/list"
        res = requests.get(url, headers=self.headers, verify=False).json()
        chapters = res["data"]
        for item in chapters:
            id = item["id"]
            chapter_name = item["name"]
            print(chapter_name)
            content = self.get_comtent(book_id, id)
            params = (id, chapter_name, content, book_id)
            sqlstr = "insert into chapter values (%s,%s,%s,%s)"
            self.cursor.execute(sqlstr, params)
            self.conn.commit()

    def close(self):
        self.conn.close()

    def handle_book_detail(self, id):
        url = f"https://api-freesy.jinhuyu.cn/api/book/{id}"
        res = requests.get(url, headers=self.headers, verify=False).json()
        return int(res["data"]["view_count"]), int(res["data"]["word_count"])

    def get_comtent(self, b_id, c_id):
        url = f"https://api-freesy.jinhuyu.cn/api/book/{b_id}/chapter/{c_id}"
        res = requests.get(url, headers=self.headers, verify=False).json()
        return res["data"]["content"]


if __name__ == '__main__':
    BooksSpider().start()
