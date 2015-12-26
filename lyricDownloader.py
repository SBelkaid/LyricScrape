import requests, re, time
import sqlite3
from urlparse import urljoin
from bs4 import BeautifulSoup
import logging, hashlib


logging.basicConfig(filename='logger.log',level=logging.DEBUG)
logging.getLogger("requests").setLevel(logging.WARNING)


class Downloader():
	base_url_lyric = 'https://www.musixmatch.com/lyrics/'
	
	@staticmethod
	def find_titles(artist_name, link, stored):
		"""
		:params: name of the artist
		:params: source markup
		:params: stored, already stored song titles
		:return: set of tuples containing artist_name and title
		"""
		page_count = 0
		songs = set()
		splitted_searching = artist_name.split(' ')
		possible_collaborations = set()
		while 1:
			try:
				payload = {'page': page_count, 'q_track_artist': artist_name}
				source = requests.get(link, payload)
			except UnicodeEncodeError, e:
				logging.error('UnicodeEncodeError in the first try of find_titles')
				raise e
			if source.status_code != 200:
				logging.error('Check artist name, opening url not equal 200')
				break
			soup = BeautifulSoup(source.content, 'lxml')
			source.close()
			if not soup.track_list:
				break
			tracks = soup.find_all('track')

			for song in tracks:
				try:
					if song.track_name.text in stored:
						# print 'already stored {}'.format(song.track_name.text)
						continue
					if not song.has_lyrics.text == '1':
						# print '{} doesn\'t have a lyric, continuing'.format(song.track_name.text)
						continue
					splitted_retrieved_name = song.artist_name.text.split(' ')
					# print splitted_retrieved_name, splitted_searching
					if len(splitted_searching) == len(splitted_retrieved_name) and\
					 len(splitted_searching[0]) == len(splitted_retrieved_name[0]): # heeeeeeel gaar
						songs.add((song.artist_name.text,song.track_name.text))
					if len(splitted_searching) != len(splitted_retrieved_name):
						x = re.search('(?<='+artist_name.strip('()')+' feat\. ).*', song.artist_name.text, re.I)
						if x:
							possible_collaborations.add((artist_name, x.group()))
							# logging.info('maybe add collab section in db {}'.format(possible_collaborations))
				except AttributeError, e:
					logging.error("""{} Couldn't find artist name or track name {}.
						Try in LyricDownloader.find_titles""".format(time.strftime('%D %H:%M:%S'),e))
					continue
				except UnicodeError, e:
					logging.error("""{}Always some unicode error thing {}.
					 Try in LyricDownloader.find_titles""".format(time.strftime('%D %H:%M:%S'),e))
					continue
			page_count += 1
			# print page_count, len(songs)
			if len(songs) >= 10 or page_count >= 10:
				# print 'BREAKING OUT OF THE WHILE', crawled 10 pages, enough for now..
				break

		collabs = Downloader.check_collabs(possible_collaborations)
		return songs, collabs

	@staticmethod
	def check_collabs(possible_collaborations):
		return possible_collaborations

	@staticmethod
	def return_lyrics(artist_data, db_conn, limit=10):
		'''
		:param: set of names and titles
		:return: set of tuples containing artist name, title and lyrics
		'''
		all_songs = set()
		copy_of_artist_data = artist_data.copy()
		for e in artist_data:
			if len(all_songs) == limit:
				break
			song = copy_of_artist_data.pop()
			url = urljoin(Downloader.base_url_lyric,'/'.join(song)).encode('utf-8')
			# print url
			source = requests.get(url)
			if source.status_code != 200:
				continue
			# logging.info('crawled url: {} {}'.format(time.strftime('%D:%H:%M:%S'),url)) 
			soup = BeautifulSoup(source.content, 'lxml')
			source.close()
			lyric = soup.find('span', id='lyrics-html')
			if lyric:
				# hash_val = get_md5_checksum(lyric.text)
				hash_check, hash_val = Downloader.check_already_existing(db_conn, lyric)
				if hash_check:
					continue
				all_songs.add((song[0], song[1], lyric.text, hash_val))
				# all_songs.add((song[0], song[1], lyric.text))
				time.sleep(2) #sleeping, else will be banned from the website. 
		return all_songs
	
	@staticmethod
	def get_md5_checksum(lyric):
	    '''
	    Obtains the md5 checksum out of a filename
	    '''
	    md5_hasher = hashlib.md5()
	    # fd = open(filename)
	    # buf = fd.read(65536)
	    buf = lyric.encode('utf-8')
	    # while len(buf) > 0:
	        # md5_hasher.update(buf)
	        # buf = fd.read(65536)
	    md5_hasher.update(buf)
	    # fd.close()
	    return md5_hasher.hexdigest()
	    
	@staticmethod
	def check_already_existing(db_con, lyrics):
	    '''
	    Checks if the given filename already has been indexed or not
	    '''
	    existing = True
	    checksum = Downloader.get_md5_checksum(lyrics)
	    my_query = 'SELECT * from Lyrics where hash = "%s";' % checksum
	    this_cursor = db_con.cursor()
	    results = this_cursor.execute(my_query)
	    first_hit = results.fetchone()
	    if first_hit is None:
	        #The song is not in the database
	        # logging.info('{} The document is not in the index and will be indexed'.format(time.strftime('%D:%H:%M:%S')))
	        existing = False
	    else:
	        this_id, this_has, this_timestamp = first_hit
	        # logging.info('The document is already in the index. It was created at %s' % this_timestamp)
	        existing = True
	        
	    return existing, checksum



if __name__ == '__main__':
	url = open('start_url2', 'r').read()
	c = sqlite3.connect('artistsStored.db').cursor()
	crawled = zip(*c.execute('SELECT title FROM Lyrics').fetchall())[0]
	res = Downloader.find_titles('Adele', url, crawled)
	# lyrics = Downloader.return_lyrics(res)	
