import json
import os
import argparse
from pprint import pprint

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
    parser.add_argument('--start_page', help='Страница с', type=int)
    parser.add_argument('--end_page', help='Страница по', type=int)

    args = parser.parse_args()

    # 'python parse_tululu_category.py --start_page 700 --end_page 701'

    return args.start_page, args.end_page


def main():
    logging.basicConfig(level=logging.INFO)
    logger.setLevel(logging.INFO)

    url = 'https://tululu.org'



    start_page, end_page = get_arguments()

    if end_page:
        print("Есть оба")
        for page_id in range(start_page, end_page + 1):
            print()
    else:
        url_fantasi = 'https://tululu.org/l55/'
        print("Один")
        while True:
            try:
                url_fantasi_page = f'{url_fantasi}{start_page}'
                response = requests.get(url_fantasi_page)
                response.raise_for_status()
                check_for_redirect(response)
                page_url = response.url
                print(page_url)


                soup = BeautifulSoup(response.text, 'lxml')
                         # book_cards = soup.find_all(class_='bookimage')

                book_cards_selector = '.bookimage a[href^="/b"]'
                book_cards = soup.select(book_cards_selector)
                for book_card in book_cards:
                    link = book_card.get('href')
                    _, not_sanitized_book_id = link.split('b')
                    book_id = sanitize_filename(not_sanitized_book_id.strip())
                    print(book_id)
                start_page += 1
            except HTTPError:
                break





    # for book_id in range(start_id, end_id + 1):
    #     try:
    #         response = requests.get(f'{url}/b{book_id}/')
    #         response.raise_for_status()
    #         check_for_redirect(response)
    #         page_url = response.url
    #         soup = BeautifulSoup(response.text, 'lxml')
    #         book = parse_book_page(soup)
    #         download_txt(url, book_id, book['tittle'])
    #         download_image(page_url, book['image_link'], book['image_name'])
    #         download_comments(book['comments'], book_id, book['tittle'])
    #     except HTTPError:
    #         logger.warning(f'Страница {url}/b{book_id} не существует')
    #         continue
    #     except ConnectionError:
    #         logger.warning('Потеряно соединение с интернетом')
    #         time.sleep(5)
    #         continue

    # url_fantasi = 'https://tululu.org/l55/'
    #
    # сf = []

    # for page in range(1, 2+1):
    #     print(page)
    #     try:
    #         url_fantasi_page = f'{url_fantasi}{page}'
    #         response = requests.get(url_fantasi_page)
    #         response.raise_for_status()
    #         check_for_redirect(response)
    #         page_url = response.url
    #         soup = BeautifulSoup(response.text, 'lxml')
    #         # book_cards = soup.find_all(class_='bookimage')
    #
    #         book_cards_selector = '.bookimage a[href^="/b"]'
    #         book_cards = soup.select(book_cards_selector)
    #         for book_card in book_cards:
    #
    #             link = book_card.get('href')
    #
    #             _, not_sanitized_book_id = link.split('b')
    #             book_id = sanitize_filename(not_sanitized_book_id.strip())
    #             print(book_id)
    #
    #             book_link = urljoin(page_url, link)
    #
    #
    #             response = requests.get(book_link)
    #             response.raise_for_status()
    #             check_for_redirect(response)
    #             page_url = response.url
    #
    #
    #             soup2 = BeautifulSoup(response.text, 'lxml')
    #             book = parse_book_page(soup2)
    #
    #             download_txt(url, book_id, book['tittle'])
    #             download_image(page_url, book['image_link'], book['image_name'])
    #             download_comments(book['comments'], book_id, book['tittle'])
    #
    #
    #
    #
    #             сf.append(parse_book_page(soup2))
    #
    #         page = page + 1
    #         print(page)
    #
    #
    #
    #
    #     except requests.exceptions.HTTPError:
    #         break

    # with open('filename', 'w', encoding='utf8') as json_file:
    #         json.dump(сf, json_file, ensure_ascii=False)




















if __name__ == '__main__':
    main()
