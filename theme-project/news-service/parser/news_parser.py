from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import json



BASE_URL = 'https://www.omgtu.ru/news/'
DATA_PATH = './data'

def get_news_id(url):
    index = url.find('eid=')
    return url[index + 4 : ]

def download_image(session, img_url, folder):
    try:
        response = session.get(img_url, timeout=10, stream=True)
        response.raise_for_status()
        
        filename = f"image.jpg"
        filepath = os.path.join(folder, filename)
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return filename
    except Exception as e:
        print(f"  Ошибка загрузки изображения: {e}")
        return None
    
def get_news():
    session = requests.Session()    
    response = session.get(BASE_URL, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    all_news = []
    news_cards = soup.find_all('div', class_='news-card')

    for card in news_cards:
        img_tag = card.find('img')
        img_src = img_tag.get('src')
        img_url = urljoin(BASE_URL, img_src)
        link_tag = card.find('a', href=True)
        href = link_tag['href']
        news_url = urljoin(BASE_URL, href)

        news_id = get_news_id(news_url)

        title = img_tag.get('alt') or img_tag.get('title') or ''

        date_tag = card.find('div', class_='news-card__date')
        date = date_tag.text.strip()
        image_file = None
        try:
            news_folder = os.path.join(f"{DATA_PATH}", f'images/{news_id}')
            os.makedirs(news_folder, exist_ok=True)
            image_file = download_image(session, img_url, news_folder)
        except Exception as e:
            print(f'Ошибка при загрузке изображения: {e}')

        # print(f'Новость {news_id}: Содержание: {title[:10]}, Дата: {date}, Изображение: {img_url}, Ссылка: {news_url}')

        all_news.append({
            'id': news_id,
            'title': title,
            'date': date,
            'image': image_file,
            'url': news_url
        })
    return all_news

def load_news(all_news):
    with open(f'{DATA_PATH}/news.json', 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    all_news = get_news()
    load_news(all_news)