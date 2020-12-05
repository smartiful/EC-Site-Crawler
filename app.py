import os
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

driver = webdriver.Chrome()
driver.get(BASE_URL)


class EcSiteCrawler():
    def __init__(self):
        self.logger = logger
        self.all_category_url = self.get_all_category_url()

    # downloader
    def downloader(self, iamge_url: str, category: str) -> int:
        if 'p_gtype=2' in category:
            file_path = f'./image_data{category.replace("?p_gtype=2", "used")}'
        else:
            file_path = f'./image_data{category}'
        result = requests.get(iamge_url)
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        with open(file_path + iamge_url[iamge_url.rindex("/"):], 'wb') as outfile:
            outfile.write(result.content)
        self.logger.success(f'url :{iamge_url} | category: {category}')

    # decode and parse url
    def soup_url(self, url: str) -> BeautifulSoup:
        result = requests.get(url)
        result.encoding = result.apparent_encoding
        soup = BeautifulSoup(result.text, "html.parser")
        return soup

    # get all category url
    def get_all_category_url(self) -> list:
        category_url_list = []
        zozotown_soup = self.soup_url(ZOZOTOWN_CATEGORY_URL)
        h2 = zozotown_soup.find_all('h2')
        for tag in h2:
            category_url = BASE_URL + tag.a.get('href')
            category_url_list.append(category_url)

        zozoused_soup = self.soup_url(ZOZOUSED_CATEGORY_URL)
        h2 = zozoused_soup.find_all('h2')
        for tag in h2:
            category_url = BASE_URL + tag.a.get('href')
            category_url_list.append(category_url)

        with open('./data/all_category_url.txt', 'w') as f:
            for url in category_url_list:
                f.write(url)
                f.write('\n')

        return category_url_list

    # get category product url
    def get_category_product_url(self) -> list:
        product_url_list = []
        count_product = len(driver.find_elements_by_xpath(
            '//*[@id="searchResultList"]/li/div/a')) + 1

        for product in range(1, count_product):
            product_url = driver.find_element_by_xpath(
                f'//*[@id="searchResultList"]/li[{product}]/div/a').get_attribute('href')
            # pass AD pages
            if 'e.s4p.jp' not in product_url:
                product_url_list.append(product_url)
        return product_url_list

    # get category name from product page
    def get_category_name(self) -> str:
        category_url = driver.find_element_by_xpath(
            '//*[@id="breadCrumb"]/ul/li[2]/a').get_attribute('href')
        category_name = category_url.replace('https://zozo.jp', '')
        return category_name

    def dump_next_page(self):
        try:
            if driver.find_element_by_class_name('next'):
                driver.find_element_by_class_name('next').click()
        except NoSuchElementException:
            return False
        return True

    # download image from product page
    def get_product_image(self, product_url: str) -> list:
        image_list = []
        driver.get(product_url)
        category_name = self.get_category_name()
        image_count = len(
            driver.find_element_by_id('photoThimb').find_elements_by_tag_name('li')) + 1

        for image in range(1, image_count):
            image_url = driver.find_element_by_xpath(
                f'//*[@id="photoThimb"]/li[{image}]/div/span/img').get_attribute('src')
            image_url = image_url.replace('35', '500')

            image_list.append(image_url)
        return image_list

        #self.downloader(image_url, category_name)

    # start crawler
    def start_crawler(self):
        # 1. get all category url
        # 2. get product url list from category url
        # 3. download image from product page
        # 4. jump to next product page
        # 5. jump to next category url
        for category_url in self.all_category_url:
            print(category_url)
            driver.get(category_url)
            product_url_list = self.get_category_product_url()
            for product_url in product_url_list:
                image_url_list = self.get_product_image(product_url)
                category_name = self.get_category_name()
                for image_url in image_url_list:
                    self.downloader(image_url, category_name)
            if self.dump_next_page():
                self.dump_next_page()
            else:
                break
