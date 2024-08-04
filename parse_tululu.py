import os
import argparse
import requests
from pathlib import Path
from requests import HTTPError
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
import logging
import time
from urllib.parse import urljoin


logger = logging.getLogger('Logger')


def check_for_redirect(response):
            if response.history:
                raise HTTPError


def download_txt(url, book_id, tittle, folder='books/'):
    filename = f'{book_id}. {tittle}'
    url = f"{url}/txt.php"
    payload_txt = {'id': book_id}
    response = requests.get(url, params=payload_txt)
    response.raise_for_status()
    check_for_redirect(response)

    Path(folder).mkdir(parents=True, exist_ok=True)
    filepath_without_format = os.path.join(folder, sanitize_filename(filename))
    filepath = f'{filepath_without_format}.txt'
    with open(filepath, 'w') as file:
        file.write(response.text)

    return filepath


def download_image(page_url, image_link, filename, folder='images/'):
    url = urljoin(page_url, image_link)
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)

    Path(folder).mkdir(parents=True, exist_ok=True)
    filepath = os.path.join(folder, sanitize_filename(filename))
    with open(filepath, 'wb') as file:
        file.write(response.content)

    return filepath


def download_comments(comments, book_id, tittle, folder='comments/'):
    filename = f'{book_id}. {tittle} - комментарии'
    Path(folder).mkdir(parents=True, exist_ok=True)
    filepath_without_format = os.path.join(folder, sanitize_filename(filename))
    filepath = f'{filepath_without_format}.txt'
    with open(filepath, 'w') as file:
        file.writelines(f"{comment}\n" for comment in comments)

    return filepath


def parse_book_page(soup):
    not_sanitized_tittle, not_sanitized_author = soup.find('h1').text.split('::')
    tittle = sanitize_filename(not_sanitized_tittle.strip())
    author = sanitize_filename(not_sanitized_author.strip())

    comments_tag = soup.find_all(class_='texts')
    comments = [comment.find(class_='black').text for comment in comments_tag]

    genre_tag = soup.find('span', class_='d_book').find_all('a')
    genres = [genre.text for genre in genre_tag]

    image_link = soup.find(class_='bookimage').find('img')['src']
    image_name = image_link.split('/')[-1]
    book = {'tittle' : tittle,
            'author' : author,
            'comments' : comments,
            'genres' : genres,
            'image_name' :image_name,
            'image_link' : image_link}

    return book


def get_arguments():
    parser = argparse.ArgumentParser(
        description='Скачивание заданных страниц'
    )
    parser.add_argument('start_id', help='Страница с', type=int)
    parser.add_argument('end_id', help='Страница по', type=int)
    args = parser.parse_args()

    return args.start_id, args.end_id


def download_books(url, books_id):
    for book_id in books_id:
        try:
            response = requests.get(f'{url}/b{book_id}/')
            response.raise_for_status()
            check_for_redirect(response)
            page_url = response.url
            soup = BeautifulSoup(response.text, 'lxml')
            book = parse_book_page(soup)
            download_txt(url, book_id, book['tittle'])
            download_image(page_url, book['image_link'], book['image_name'])
            download_comments(book['comments'], book_id, book['tittle'])
        except HTTPError:
            logger.warning(f'Страница {url}/b{book_id} не существует')
            continue
        except ConnectionError:
            logger.warning('Потеряно соединение с интернетом')
            time.sleep(5)
            continue

def get_books_id(url, genre_id , start_page, end_page = None):
    if end_page:
        books_id = []
        for page in range(start_page, end_page+1):
            url_genre_page = f'{url}/l{genre_id}/{page}'
            response = requests.get(url_genre_page)
            response.raise_for_status()
            check_for_redirect(response)
            soup = BeautifulSoup(response.text, 'lxml')

            book_cards_selector = '.bookimage a[href^="/b"]'
            book_cards = soup.select(book_cards_selector)
            for book_card in book_cards:
                link = book_card.get('href')

                _, not_sanitized_book_id = link.split('b')
                book_id = sanitize_filename(not_sanitized_book_id.strip())
                books_id.append(book_id)
        return books_id


    else:
        books_id = []
        while True:
            try:
                url_genre_page = f'{url}/l{genre_id}/{start_page}'
                response = requests.get(url_genre_page)
                response.raise_for_status()
                check_for_redirect(response)
                page_url = response.url
                print(page_url)

                soup = BeautifulSoup(response.text, 'lxml')

                book_cards_selector = '.bookimage a[href^="/b"]'
                book_cards = soup.select(book_cards_selector)

                for book_card in book_cards:
                    link = book_card.get('href')

                    _, not_sanitized_book_id = link.split('b')
                    book_id = sanitize_filename(not_sanitized_book_id.strip())
                    books_id.append(book_id)

                start_page += 1
            except HTTPError:
                logger.warning(f'Страница {url_genre_page} не существует')
                return books_id











def main():
    logging.basicConfig(level=logging.INFO)
    logger.setLevel(logging.INFO)

    url = 'https://tululu.org'
    genre_id = 55
    start_page = 700




    books_id = get_books_id(url, genre_id , start_page)
    print(books_id)

    download_books(url, books_id)






if __name__ == '__main__':
    main()
