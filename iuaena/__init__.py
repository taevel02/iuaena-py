#!/usr/bin/python3

import json
import sqlite3
import time
from datetime import datetime
from requests import get
from selenium import webdriver
from bs4 import BeautifulSoup as bs

URL = 'https://m.cafe.daum.net/IU'
BOARD_NAMES = {
    'NDuY': '전체공지',
    'Lqm5': '카페공지',
    'NmPv': '이벤트',
    'Lqm8': '공방참여',
    'LqmF': '자유게시판',
    'NjSn': '2030게시판',
    'LqmG': '모니터후기',
    'QdKy': '친목나눔',
    'NHRM': '원본사진',
    'NHRN': '영상음성',
    'NHRL': '회원작품',
    'RBOf': '응원투표',
    'LqmO': '정보기사',
    'NHRO': '인증자랑'
}

latest_num = 0
post_num = 0
driver = webdriver.Chrome('../chromedriver')

with open('../config.json', 'r') as f:
    config = json.load(f)


def cbn(board_name):
    return BOARD_NAMES.get(board_name, '???')


def fmt(date):
    return date and date.strftime('%Y-%m-%d %H:%M:%S')


class Iuaena:
    def __init__(self, url=URL):
        self.url = url

    def soup(self, url, driver_disabled=False):
        if driver_disabled:
            driver.get(url)
            return bs(driver.page_source, 'html.parser')
        else:
            return bs(get(url).text, 'html.parser')

    def fetch(self, board_name='/_rec'):
        return self.get_article_info(board_name)

    def get_article_info(self, board_name):
        global latest_num
        global post_num

        soup = self.soup(self.url + str(board_name), False)
        posts = soup.select('li')
        post_href = posts[3].find('a', class_='link_cafe').attrs['href']
        board_name = post_href[4:8]
        post_num = int(post_href[9:].replace('?', ''))
        url = 'https://m.cafe.daum.net' + post_href
        self.create_db(board_name)
        # return post_href, board_name, post_num, url

        if latest_num != post_num:
            latest_num = post_num

            soup = self.soup(url, True)
            title = soup.find('h3', class_='tit_subject')
            if title is not None:
                title = title.get_text(strip=True)
            nick = soup.find('span', class_='sr_only').next_sibling
            contents = soup.find('div', id='article').get_text('\n', strip=True)

            self.write_db(board_name, post_num, fmt(datetime.now()), title, nick, contents, url)
            return fmt(datetime.now()), title, nick, url
        else:
            return '새로운 게시물이 없습니다.'

    def create_db(self, board_name):
        conn = sqlite3.connect('../log.db')
        cur = conn.cursor()
        sql = 'CREATE TABLE IF NOT EXISTS "' + cbn(board_name) + \
              '"("num" INTEGER NOT NULL UNIQUE, "date" TEXT, "title" TEXT, ' \
              '"nickname" TEXT, "content" TEXT, "url" TEXT);'
        cur.execute(sql)
        conn.commit()
        conn.close()

    def write_db(self, board_name, num, date, title, nick, content, url):
        conn = sqlite3.connect('../log.db')
        cur = conn.cursor()
        sql = "replace into %s(num, date, title, nickname, content, url) values (?, ?, ?, ?, ?, ?)" % cbn(board_name)
        cur.execute(sql, (num, date, title, nick, content, url))
        conn.commit()
        conn.close()


if __name__ == '__main__':
    email = config['KAKAO']['EMAIL'],
    password = config['KAKAO']['PASSWORD']

    driver.get('https://logins.daum.net/accounts/loginform.do?status=-401&url=https%3A%2F%2Fm.cafe.daum.net%2F')
    time.sleep(1)
    driver.find_element_by_xpath("""//*[@id="mArticle"]/div/div/div/div[3]/a[1]""").click()
    time.sleep(1)
    driver.find_element_by_xpath("""//*[@id="id_email_2"]""").send_keys(email)
    driver.find_element_by_xpath("""//*[@id="id_password_3"]""").send_keys(password)
    driver.find_element_by_xpath("""//*[@id="login-form"]/fieldset/div[8]/button[1]""").click()
    time.sleep(1)

    while True:
        print(Iuaena().fetch(board_name='/_rec'))
        time.sleep(20)
