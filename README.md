# EC-Site-Crawler

## ①安装pip库

```
pip install -r requirements.txt
```

## ②设置ChromeDriver

### 1. 在 https://chromedriver.chromium.org/downloads 下载对应Chrome浏览器内核版本的ChromeDriver.exe
### 2. 把ChromeDriver.exe文件放到python.exe的同一路径里面，比如 H:\Python38\ChromeDriver.exe
### 3. 修改app.py文件中的ChromeDriver.exe路径

```
driver = webdriver.Chrome(options=options,
                          executable_path=r'[在这里替换路径]')
```

## ③爬取网站图片

```
python app.py
```
