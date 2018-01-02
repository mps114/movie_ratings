import requests 
from bs4 import BeautifulSoup
from collections import OrderedDict
import json
import csv
import argparse

def main():
	movie_list = []
	url = "https://www.rottentomatoes.com/browse/in-theaters/"
	movies_page = requests.get(url)
	movies_soup = BeautifulSoup(movies_page.content, 'html.parser')
	print(movies_soup.prettify())
	"""simple_html_movies = movies_soup.find(type="application/ld+json")
	loaded_movies_link = json.loads(simple_html_movies.text)['itemListElement']
	for individual_movie in loaded_movies_link:
		movie_list.append(individual_movie['url'])
	print(movie_list)"""


main()