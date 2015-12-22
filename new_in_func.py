import pickle

# data = pickle.load(open('input_new_func.pickle', 'r'))
data2 = pickle.load(open('input2_new_func.pickle', 'r'))
found_artist_names = data2

def find_titles(artist_name, link=None, stored = None):
	splitted_searching = artist_name.split(' ')
	for i in found_artist_names:
		splitted_retrieved_name = i.split(' ')
		if len(splitted_searching) == len(splitted_retrieved_name) and\
		 len(splitted_searching[0]) == len(splitted_retrieved_name[0]):
			print splitted_searching, splitted_retrieved_name


		else:
			# print splitted_searching, i
			pass


find_titles('Adele')

