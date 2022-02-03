import csv
import requests
from bs4 import BeautifulSoup


HOME = 'http://books.toscrape.com'

RATINGS = {
    'One': 1,
    'Two': 2,
    'Three': 3,
    'Four': 4,
    'Five': 5
}

HEADER = [
    'product_page_url',
    'universal_product_code (upc)',
    'title',
    'price_including_tax',
    'price_excluding_tax',
    'number_available',
    'product_description',
    'category',
    'review_rating',
    'image_url'
]

all_data = []


def scrap_one_product(home: str, url: str, ratings: list) -> list:
    """Récupération des infos d'un produit via url"""
    data = []
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    table = soup.find('table', class_='table-striped')
    tds = table.find_all('td')

    # product page url
    data.append(url)
    # upc
    data.append(tds[0].string)
    # title
    data.append(soup.find('div', class_='product_main').find('h1').string)
    # price including tax
    data.append(tds[2].string)
    # price excluding tax
    data.append(tds[3].string)
    # number available
    data.append(tds[5].string)
    # product description
    data.append(soup.find(id='product_description').find_next('p').string)
    # category
    data.append(soup.find('ul', class_='breadcrumb').find_all('li')[2].find('a').string)
    # review rating
    data.append(ratings[soup.find('p', class_='star-rating').attrs['class'][1]])
    # image url
    data.append(home + soup.find(id='product_gallery').find('img').attrs['src'].replace('../../', '/'))

    return data


def save_to_csv(csv_header: list, data: list):
    with open('one_category.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(csv_header)
        for d in data:
            writer.writerow(d)


category = 'Fiction'
books_urls = []
page_contains_book = True
page_number = 1
while page_contains_book:
    page = requests.get('https://books.toscrape.com/catalogue/category/books/fiction_10/page-' + str(page_number) + '.html')
    if page.status_code != 200:
        break
    soup = BeautifulSoup(page.content, 'html.parser')
    products = soup.find_all('article', class_='product_pod')
    
    for product in products:
        product_url = HOME + product.find('a').attrs['href'].replace('../../../', '/catalogue/')
        one_data = scrap_one_product(HOME, product_url, RATINGS)
        all_data.append(one_data)

    save_to_csv(HEADER, all_data)

    page_number += 1
