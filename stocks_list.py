import re
import pymongo
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# 定义MongoDB数据库
client = pymongo.MongoClient('localhost',27017)
db = client['stocks']
collection = db['list']

# 设置无头浏览器
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
browser = webdriver.Chrome(chrome_options=chrome_options)

#调试使用
# browser = webdriver.Chrome()

wait = WebDriverWait(browser, 10)


# 得到页码数
def page():
    try:
        browser.get('http://quote.eastmoney.com/center/gridlist.html#neeq_stocks')
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#main-table'))
        )
        pages = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#main-table_paginate_page > a:nth-child(7)'))
            )
        return pages.text
    except TimeoutException:
        return page()


# 实现跳页
def next_page(page_numbers):
    try:
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#main-table_paginate > input'))
            )
        submit = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#main-table_paginate > a'))
        )
        input.clear()
        input.send_keys(page_numbers)
        submit.click()
        wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#main-table_paginate_page > a.paginate_button.current'),str(page_numbers))
        )
    except TimeoutException:
        next_page(page_numbers)


# 解析内容page(1-23)
def parse_page_one():
    response = etree.HTML(browser.page_source)
    items = response.xpath('//*[@id="main-table"]/tbody')
    for item in items:
        rank = item.xpath('.//td[@class=" listview-col-number"]//text()')
        code = item.xpath('.//td[@class=" listview-col-Code"]/a/text()')
        url = item.xpath('.//td[@class=" listview-col-Code"]/a/@href')
        name = item.xpath('.//td[@class=" listview-col-Name"]/a/text()')
        post_bar = item.xpath('.//td[@class=" listview-col-Links"]/a[1]/@href')
        forum = item.xpath('.//td[@class=" listview-col-Links"]/a[2]/@href')
        new_price = item.xpath('.//td[@class=" listview-col-Close"]//text()')
        change = item.xpath('.//td[@class=" listview-col-Change"]//text()')
        change_percent = item.xpath('.//td[@class="listview-col-ChangePercent sorting_1"]//text()')
        volume = item.xpath('.//td[@class=" listview-col-Volume"]/text()')
        amount = item.xpath('.//td[@class=" listview-col-Amount"]/text()')
        previous_close = item.xpath('.//td[@class=" listview-col-PreviousClose"]/text()')
        today_open = item.xpath('.//td[@class=" listview-col-Open"]//text()')
        high = item.xpath('.//td[@class=" listview-col-High"]//text()')
        low = item.xpath('.//td[@class=" listview-col-Low"]//text()')
        commission_rate = item.xpath('.//td[@class=" listview-col-CommissionRate"]//text()')

        for item in range(len(rank)):

            yield{
             'rank': rank[item],
             'code': code[item],
             'url': url[item],
             'name': name[item],
             'post_bar': post_bar[item],
             'forum': forum[item],
             'new_price': new_price[item],
             'change': change[item],
             'change_percent': change_percent[item],
             'volume': volume[item],
             'amount': amount[item],
             'previous_close': previous_close[item],
             'today_open': today_open[item],
             'hige': high[item],
             'low': low[item],
             'commission_rate': commission_rate[item]
            }

# 解析内容page(24-pages)
def parse_page_two():
    response = etree.HTML(browser.page_source)
    items = response.xpath('//*[@id="main-table"]/tbody')
    for item in items:
        rank = item.xpath('.//td[@class=" listview-col-number"]//text()')
        code = item.xpath('.//td[@class=" listview-col-Code"]/a/text()')
        url = item.xpath('.//td[@class=" listview-col-Code"]/a/@href')
        name = item.xpath('.//td[@class=" listview-col-Name"]/a/text()')
        post_bar = item.xpath('.//td[@class=" listview-col-Links"]/a[1]/@href')
        forum = item.xpath('.//td[@class=" listview-col-Links"]/a[2]/@href')
        previous_close = item.xpath('.//td[@class=" listview-col-PreviousClose"]/text()')

        for item in range(len(rank)):

            yield {
                'rank': rank[item],
                'code': code[item],
                'url': url[item],
                'name': name[item],
                'post_bar': post_bar[item],
                'forum': forum[item],
                'previous_close': previous_close[item]
            }


def main():
    pages = int(page())
    for i in range(1, 24):
        next_page(i)
        for item in parse_page_one():
            collection.insert(item)
        print('第{}页正在保存到MongoDB。'.format(i))

    for i in range(24, pages):
        next_page(i)
        for item in parse_page_two():
            collection.insert(item)
        print('第{}页正在保存到MongoDB。'.format(i))


if __name__ == "__main__":
    main()










