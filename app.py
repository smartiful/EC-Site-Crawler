import os
import requests
import urllib.request
from selenium import webdriver

BASE_URL = 'https://zozo.jp'
ZOZOTOWN_CATEGORY_URL = BASE_URL + '/category/'
ZOZOUSED_CATEGORY_URL = BASE_URL + '/zozoused/category/'


driver = webdriver.Chrome()
driver.get('https://zozo.jp/')


def downloader(iamge_url: str, category: str) -> int:
    result = requests.get(iamge_url)
    file_path = f'.{category}'
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    with open(file_path + iamge_url[iamge_url.rindex("/"):], 'wb') as outfile:
        outfile.write(result.content)
    return 'ok'


def get_all_category_url():
    pass


def get_category_product_url() -> list:
    product_url_list = []

    count_product = len(driver.find_elements_by_xpath(
        '//*[@id="searchResultList"]/li/div/a')) + 1

    for product in range(1, count_product):
        product_url = driver.find_element_by_xpath(
            f'//*[@id="searchResultList"]/li[{product}]/div/a').get_attribute('href')
        if 'e.s4p.jp' not in product_url:
            product_url_list.append(product_url)
    return product_url_list


def get_category_name() -> str:
    category_url = driver.find_element_by_xpath(
        '//*[@id="breadCrumb"]/ul/li[2]/a').get_attribute('href')
    category_name = category_url.replace('https://zozo.jp', '')
    return category_name


def get_product_image_url(product_url_list: list) -> list:
    image_url_list = []
    for url in product_url_list:
        # 跳转到商品详情页
        driver.get(url)

        # 列出商品详情页的图片数量
        image_count = len(driver.find_element_by_id(
            'photoThimb').find_elements_by_tag_name('li')) + 1

        # 获取商品详情页的所有图片URL, 并更改为大图片
        for image in range(1, image_count):
            image_url = driver.find_element_by_xpath(
                f'//*[@id="photoThimb"]/li[{image}]/div/span/img').get_attribute('src')
            image_url = image_url.replace('35', '500')
            image_url_list.append(image_url)
    return image_url_list
