import os
import re
import trio
import json
import httpx
import random
import asyncio
import requests
import urllib.request
from loguru import logger
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


BASE_URL = 'https://zozo.jp'
ZOZOTOWN_CATEGORY_URL = BASE_URL + '/category/'
ZOZOUSED_CATEGORY_URL = BASE_URL + '/zozoused/category/'
logger.add(
    "./logs/{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    level='DEBUG', encoding='utf-8'
)


options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
prefs = {"profile.default_content_setting_values.notifications": 2}
options.add_experimental_option("prefs", prefs)
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_argument(
    "service_args=['–ignore-ssl-errors=true', '–ssl-protocol=TLSv1']")

# ip:port
PROXY = "110.77.134.112"
# 设置代理IP
options.add_argument('--proxy-server=http://%s' % PROXY)

driver = webdriver.Chrome(options=options,
                          executable_path=r'H:\Python38\chromedriver.exe')

with open('./data/fake_user_agent.txt', 'r') as f:
    user_agent_list = json.load(f)


class EcSiteCrawler():
    def __init__(self):
        self.all_category_url = self.get_all_category_url()

    # downloader
    async def downloader(self, image_url: str, category: str, product_id: str) -> int:
        category = re.sub(r"[,.!?:;'|\\【】]", "", category)
        file_path = f'./image_data/{category}{product_id}'

        if not os.path.exists(file_path):
            os.makedirs(file_path)
            logger.info(f'created path {file_path}')
        try:
            async with httpx.AsyncClient() as client:
                result = await client.get(image_url, headers={'User-Agent': random.choice(user_agent_list)})
                with open(file_path + image_url[image_url.rindex("/"):], 'wb') as f:
                    f.write(result.content)
                    logger.success(f'url: {image_url} | category: {category} ')
        except Exception as e:
            logger.error(e)

    # decode and parse url
    def soup_url(self, url: str) -> BeautifulSoup:
        result = requests.get(url)
        result.encoding = result.apparent_encoding
        soup = BeautifulSoup(result.text, "html.parser")
        logger.success(f'Requested url: {url}')
        return soup

    # get all category url
    def get_all_category_url(self) -> list:
        category_url_list = []

        zozotown_soup = self.soup_url(ZOZOTOWN_CATEGORY_URL)
        h2 = zozotown_soup.find_all('h2')
        for tag in h2:
            category_url = BASE_URL + tag.a.get('href')
            category_url_list.append(category_url)
            logger.success(f'find category url: {category_url}')

        zozoused_soup = self.soup_url(ZOZOUSED_CATEGORY_URL)
        h2 = zozoused_soup.find_all('h2')
        for tag in h2:
            category_url = BASE_URL + tag.a.get('href')
            category_url_list.append(category_url)
            logger.success(f'find category url: {category_url}')

        return category_url_list

    # get category product url
    def get_category_product_url(self) -> list:
        product_url_list = []

        count_product = len(driver.find_elements_by_xpath(
            '//*[@id="searchResultList"]/li/div/a')) + 1

        for product in range(1, count_product):
            product_url = driver.find_element_by_xpath(
                f'//*[@id="searchResultList"]/li[{product}]/div/a').get_attribute('href')
            product_id = re.findall("\d+", product_url)[0]
            # pass AD url and duplicate product
            if 'e.s4p.jp' not in product_url and any(product_id in url for url in product_url_list) == False:
                product_url_list.append(product_url)
                logger.success(f'find product url: {product_url}')
        return product_url_list

    # get category name from product page
    async def get_category_name(self) -> str:
        category_name = driver.find_element_by_xpath(
            '//*[@id="itemDetailInfo"]/div/dl/dd[2]/ul').text
        category_name = category_name.replace(
            '/', '&').replace('>\n', '/') + '/'
        return category_name

    # download image from product page
    async def get_product_image(self, product_url: str) -> list:
        image_list = []
        driver.get(product_url)
        image_count = len(
            driver.find_element_by_id('photoThimb').find_elements_by_tag_name('li')) + 1

        for image in range(1, image_count):
            image_url = driver.find_element_by_xpath(
                f'//*[@id="photoThimb"]/li[{image}]/div/span/img').get_attribute('src')
            image_url = image_url.replace('35', '500')
            image_list.append(image_url)
        return image_list

    # download product image
    def download_product_image(self, product_url: str):
        try:
            image_url_list = asyncio.run(self.get_product_image(product_url))
            category_name = asyncio.run(self.get_category_name())
            product_id = re.findall("\d+", product_url)[0]
            for image_url in image_url_list:
                trio.run(self.downloader, image_url, category_name, product_id)
        except Exception as e:
            logger.error(e)

    # start crawler
    def start_crawler(self):
        logger.info('start crawler')
        for category_url in self.all_category_url:
            driver.get(category_url)
            index = 1
            logger.info(f'start crawling category pages: {category_url}')

            while True:
                index_url = category_url + '?pno=' + str(index)
                product_url_list = self.get_category_product_url()

                for product_url in product_url_list:
                    self.download_product_image(product_url)

                driver.get(index_url)
                try:
                    driver.find_element_by_class_name('next').click()
                    index += 1
                    logger.info(f'dump to next page {index}')
                except NoSuchElementException:
                    logger.info(f'last page {index}')
                    break


start = EcSiteCrawler()
start.start_crawler()
