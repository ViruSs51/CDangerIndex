from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import json
from markdownify import markdownify as md


class News:
    def __init__(self, main_url: str, site: str, n_news: int) -> None:
        '''
        main_url: link to website with news;
        site: name of site(list: agora);
        n_news: how much news do you want to get;
        '''
        self.init_driver()

        self.url = main_url
        self.site = site
        self.n_news = n_news

        self.__getDateForAgora()

    def init_driver(self):
        service = Service('chromedriver/chromedriver.exe')
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920x1080") 
        self.__driver = webdriver.Chrome(service=service, options=chrome_options)

    def __getDateForAgora(self) -> list:
        self.datetime_now = datetime.now()
        date_now = [self.datetime_now.year, self.datetime_now.month, self.datetime_now.day]

        return date_now

    def __minusDays(self, days: int) -> list:
        datetime_date = self.datetime_now - timedelta((days))

        date = [datetime_date.year, datetime_date.month, datetime_date.day]

        return date

    @classmethod
    def haveAccesToUrl(cls, response: requests.Response) -> bool:
        if response.status_code != 200:
            return False

        return True
    
    def get_data(self) -> dict:
        pages = self.parseNews(url=self.url, pars_type='news')

        return pages

    def parseNews(self, url: str, pars_type: str) -> dict|BeautifulSoup|None:
        '''
        url: link to page;
        pars_type: type of parse(news, page)
        '''
        response = requests.get(url=url)

        if self.haveAccesToUrl(response=response):
            if pars_type.lower() == 'news':
                if self.site.lower() == 'agora': 
                    return self.__agoraNews()
            
            elif pars_type.lower() == 'page':
                self.__driver.get(url=url)

                html_content = self.__driver.page_source
                soup = BeautifulSoup(html_content, 'html.parser')

                return soup.body
                
        return None
    
    def __agoraNews(self) -> dict:
        data = {}

        #for n in range(400, self.n_news+400):
        for n in range(0, self.n_news):
            try:
                date_for_url = [('0' + e) if len(e) == 1 else e for e in map(str, self.__minusDays(n))]
                date =  map(str, self.__minusDays(n))
                for_link_date = ('' if self.url[-1] == '/' else '/') + '-'.join(date)
                for_url_date = '/'.join(date_for_url) + '/'
                print(for_url_date)
                url = self.url + for_link_date
    
                body_content = self.parseNews(url=url, pars_type='page')
                links = body_content.find_all('a')
            except Exception as err:
                print(err)

            news_data = []
            open_link = []
            for link in links:
                href = link.get('href')
                if href and for_url_date in href:
                    href_news_url = href if 'https://agora.md' in href else 'https://agora.md' + href

                    if href_news_url in open_link: continue
                    open_link.append(href_news_url)

                    print(href_news_url)
                    try:
                        news_data.append(str(self.parseNews(url=href_news_url, pars_type='page')))
                    except Exception as err:
                        print(err)
                
                    self.__driver.close()
                    self.init_driver()
            
            data[url] = news_data
            
        return data
        
news_file_name = 'data/news_data.json'
news_markdown_name = 'data/news_markdown_data.json'

def collect_news(file_name: str, main_url: str, site: str, n_news: int):
    news = News(main_url, site, n_news)
    new_news_data = news.get_data()

    file_name = 'data/news_data.json'

    try:
        with open(file_name, 'r', encoding='utf-8') as json_file:
            existing_news_data = json.load(json_file)
    except FileNotFoundError:
        existing_news_data = {}

    combined_news_data = {**existing_news_data, **new_news_data}

    with open(file_name, 'w', encoding='utf-8') as json_file:
        json.dump(combined_news_data, json_file, indent=4)

def to_markdown(news_file_name: str, markdown_file_name: str):
    try:
        with open(news_file_name, 'r', encoding='utf-8') as json_file:
            news_data = json.load(json_file)
    except FileNotFoundError:
        news_data = {}

    converted_data = {}

    i = 0
    for url in news_data:
        print(i)

        news_date = []
        for page in news_data[url]:
            news_date.append(md(page))
        
        converted_data[url] = news_date

        i += 1

    with open(markdown_file_name, 'w', encoding='utf-8') as json_file:
        json.dump(converted_data, json_file, indent=4)

#collect_news(file_name=news_file_name, main_url='https://agora.md/pescurt', site='agora', n_news=100)
#to_markdown(news_file_name=news_file_name, markdown_file_name=news_markdown_name)