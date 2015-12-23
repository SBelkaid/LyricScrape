import urllib, nltk, json
from urlparse import urljoin
from bs4 import BeautifulSoup
from lyricDownloader import Downloader
from collections import deque
import sqlite3
import logging 

logging.basicConfig(filename='logger.log',level=logging.DEBUG)


class Artist(object):
	conn = sqlite3.connect('artistsStored2.db')
	c = conn.cursor()
	base_url = open('start_url2', 'r').read()
	valid_link_abs = 'http'
	valid_link_rel = {'/', '.'}

	def __init__(self, artist_name):
		self.artist_name = artist_name
		self.track_titles = []
		self.lyrics = []
		self.all = 0
		self.splitters = ['feat', ',', '&']
		self.stored_songs = self.db_check()
		self.collaborations = None

	def start(self):
		titles_stored_songs = zip(*self.stored_songs)[1]
		set_track_titles, self.collaborations = Downloader.find_titles(self.artist_name, self.base_url, titles_stored_songs)
		return set_track_titles, self.collaborations
		# [self.track_titles.append(track[1]) for track in set_track_titles]
		# self.all = Downloader.return_lyrics(set_track_titles, Artist.conn)
		# [self.lyrics.append(lyric[2]) for lyric in self.all]
		# self.store_data()
		# logging.info('THESE ARE THE POSSIBLE COLLABORATIONS {}'.format(self.collaborations))
	
	def db_check(self):
		if not self.c.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='Lyrics'""").fetchone():
			self.c.execute('CREATE TABLE Lyrics (artist_name, title, lyric, hash)')
			logging.info("created a table: Lyrics")
			self.c.execute('INSERT INTO Lyrics VALUES (?,?,?,?)', (self.artist_name,'x','x','x')) #blank and bad fix
		
		if not self.c.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='Collabs'""").fetchone():
			self.c.execute('CREATE TABLE Collabs (artist_name, featured_artist)')
			logging.info('created a table: Collabs')
			# self.c.execute('INSERT INTO Lyrics VALUES (?,?)', (self.artist_name,'x'))
			
		 #awesome stuff with the LIKE en percent, sort of a re
		x = self.c.execute('SELECT * FROM Lyrics WHERE artist_name LIKE ?',('%'+self.artist_name+'%',)).fetchall()
		logging.info('these are all the occurences of the artist: {}'.format(x))
		if not x:
			self.c.execute('INSERT INTO Lyrics VALUES (?,?,?,?)', (self.artist_name,'x','x','x'))
			x = self.c.execute('SELECT * FROM Lyrics WHERE artist_name LIKE ?',('%'+self.artist_name+'%',)).fetchall()

		self.conn.commit()
		return x

	def store_data(self):
		self.c.executemany('''INSERT INTO Lyrics VALUES (?,?,?,?)''', self.all)
		self.conn.commit()
		self.c.executemany('''INSERT INTO Collabs VALUES (?,?)''', self.collaborations)
		self.conn.commit()
		logging.info("artist stored in db with {}".format(self.all))

	def normalize_link(self, link):
		"""
		handle absolute and relative links
		:param url:
		:return:
		"""
		if link.startswith(self.valid_link_abs):
			return link
		elif link[0] in self.valid_link_rel:
			return urljoin(self.basic_base, link)

if __name__ == '__main__':
	# s = set()
	# f = open('artists.txt', 'r').read().split('\n')
	a1 = Artist('David Guetta')
	x,c = a1.start()
	# # data = a1.db_check()
	

