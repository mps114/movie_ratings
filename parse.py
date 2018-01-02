import requests 
from bs4 import BeautifulSoup
from collections import OrderedDict
import json
import csv
import argparse
import pygal


def parse(movie):
	"""will parse through the websites depending on which movie the user chooses.
	   returns a json file"""

	# make a dict to store info in
	data = OrderedDict()

	# load the websites

	# load rotten tomatoes
	tomato_url = "http://www.rottentomatoes.com%s"%(movie)
	tomato_page = requests.get(tomato_url)
	tomato_soup = BeautifulSoup(tomato_page.content, 'html.parser')

	# extract rotten tomatoes info
	simple_html_tomato = tomato_soup.find(type="application/ld+json")
	loaded_tomato_link = json.loads(simple_html_tomato.text)
	movie_name = loaded_tomato_link['name']
	viewer_rating = loaded_tomato_link['contentRating']
	tomato_score = loaded_tomato_link['aggregateRating']['ratingValue']


	# Will find the IMBD website because it is a number
	# First, get rid of /m/ bc it gives trouble -> either do it here or rest of program
	edited_movie = movie[3:]
	first_imdb_url = "http://www.imdb.com/find?q=%s&s=all"%(edited_movie)
	first_imdb_page = requests.get(first_imdb_url)
	first_imdb_soup = BeautifulSoup(first_imdb_page.content, 'html.parser')

	# use try in case imbd movie just doesnt exist 
	imdb_score = ''
	try:
		simple_html_imdb1 = first_imdb_soup.find(id="pagecontent")
		simple_html_imdb2 = simple_html_imdb1.find('tr')
		simple_html_imdb3 = simple_html_imdb2.find('td')

		for a in simple_html_imdb3.find_all('a', href=True):
			imdb_url_part_2 = a['href']

		# form the URL we are working with for imbd
		imdb_url_part_1 = "http://www.imdb.com"
		imdb_url = imdb_url_part_1 + imdb_url_part_2

		# load imdb
		imdb_page = requests.get(imdb_url)
		imdb_soup = BeautifulSoup(imdb_page.content, 'html.parser')

		# extract imdb info
		imdb_score_unedited = imdb_soup.find('span', class_='rating').get_text()

		for a in imdb_score_unedited:
			if a == '/':
				break
			else:
				imdb_score += a 
	except AttributeError:
		imdb_score = 'N/A'
	# Add the info to dict and then a json file
	data.update({'Movie Name':movie_name,
				 'Rating':viewer_rating,
				 'Rotten Tomato Score':tomato_score,
				 'IMDB Score':imdb_score})
	return_data = json.dumps(data)
	return return_data

def top_movies():
	"""Will add to a list the current top movies in theatres according to rotten tomatoes"""
	movie_list = []
	url = "https://www.rottentomatoes.com/browse/in-theaters/"
	movies_page = requests.get(url)
	movies_soup = BeautifulSoup(movies_page.content, 'html.parser')
	simple_html_movies = movies_soup.find(type="application/ld+json")
	loaded_movies_link = json.loads(simple_html_movies.text)['itemListElement']
	for individual_movie in loaded_movies_link:
		movie_list.append(individual_movie['url'])
	return movie_list


def greeting():
	prompt = "Welcome to Phil's movie scores"
	prompt += "\nHere are the options:"
	prompt += "\n\tLook at a specific movie score (type: 'm')"
	prompt += "\n\tLook at the scores of the top movies in theatres with terminal output (type: 't')"
	prompt += "\n\tLook at the scores of the top movies (with specified range) in theatres with histogram output (type: 'h')"
	#prompt += "\n\tLook at the scores of the top movies (11-20) in theatres with histogram output (type: 'h2')"
	#prompt += "\n\tLook at the scores of the top movies (21-30) in theatres with histogram output (type: 'h3')"
	prompt += "\n\tQuit the program (type: 'q')"
	prompt += "\nChoice: "
	user_input = input(prompt)
	return user_input

def inputting_a_movie():
	movie_input = input("Pick a movie: ")
	user_movie = "-".join(movie_input.split())
	movie = "/m/" + user_movie
	return movie

def inputting_beginning_range():
	range_input_beginning = int(input("Pick a range (no more than 10), Begins at: "))
	return range_input_beginning
	
def inputting_end_range():	
	range_input_end = int(input("Ends at: "))
	return range_input_end

def print_movie_info(data_parsed):
	print("Movie Name: " + data_parsed['Movie Name'])
	print("Rating: " + data_parsed['Rating'])
	print("Rotten Tomato Score: " , data_parsed['Rotten Tomato Score']) # comma bc int
	print("IMDB Score: " + data_parsed['IMDB Score'])

def make_histogram(beginning_range, end_range):
	movie_list = top_movies()
	movie_list_names = []
	movie_list_rt_scores = []
	for individual_movie in movie_list[(beginning_range-1):(end_range)]:
		movie_data = parse(individual_movie)
		movie_data_parsed = json.loads(movie_data)
		movie_list_names.append(movie_data_parsed['Movie Name'])
		movie_list_rt_scores.append(movie_data_parsed['Rotten Tomato Score'])
	hist = pygal.Bar()
	movie_range = "("+str(beginning_range)+"-"+str(end_range)+")"
	hist.title = "Scores of top movies" + movie_range
	hist.x_labels = movie_list_names
	hist.x_title = "Movie"
	hist.y_title = "Scores"
	hist.add('Score', movie_list_rt_scores)
	hist.render_to_file('movie_visual.svg')

def main():
	user_input = greeting()
	if user_input == 'm':
		# user input for the movie
		movie = inputting_a_movie()
		scraped_data = parse(movie)
		# print out the info
		data_parsed = json.loads(scraped_data)
		#data_parsed = full_data_parsed['movie_info']
		print("\n\n")
		print_movie_info(data_parsed)
		print("\n\n")
		# back to the main menu
		main()
	elif user_input == 't':
		movie_list = top_movies()
		print("Here is a rundown of those movies: ")
		for i, item in enumerate(movie_list):
			top_movie_data = parse(item)
			movie_data_parsed = json.loads(top_movie_data)
			print("(",(i+1),")")
			print_movie_info(movie_data_parsed)
		#print(movie_list)

		main()
	elif user_input == 'h':
		beginning_range = inputting_beginning_range()
		end_range = inputting_end_range()
		val_checker = end_range - beginning_range
		if val_checker < 0:
			print("not proper range")
		#elif val_checker >= 10:
			#print("not proper range")
		else:
			make_histogram(beginning_range, end_range)
		main()
	elif user_input == 'q':
		print("thanks for using!")
	else:
		print("not an option")
		main()

main()


	




