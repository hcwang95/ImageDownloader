import urllib
import httplib
import requests
import os
import re
import time
import Cookie
from pyvirtualdisplay import Display
from selenium import webdriver
import multiprocessing
import random
import sys
from socket import error as SocketError
import errno


'''session = requests.Session()
#session.header = {
#        'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
#        "Accept-Encoding": "gzip, deflate, sdch",
#    }
url = 'https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcQYCTfvCbaGExSMJqo1OKIK674wMASShjV-Y8ycNrTGHY6k73o62Q'
response = session.get(url)
print (response.headers)

filename = os.path.join("results", str(1) + ".jpg")
with open(filename,"wb") as f:
	f.write(response.content)'''

def multiPara_wrapper(args):
	return _download(*args)


def setupSession():
	session = requests.Session()
	session.header = { 'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0","Accept-Encoding": "gzip, deflate, sdch"}
	return session
class GoogleDownloader():
	def __init__(self,word,size,browser):
		self.word = word
		self.size = size
		self.main(self.word,self.size,browser)

	def main(self, word, size, browser):
		print (word)
		wordSearch =''
		subcategory = word.split(' ')
		wordSearch =subcategory[0]
		if len(subcategory[1:]) >= 1:
			for pt in subcategory[1:]:
				wordSearch += "+" + pt
		print (wordSearch)
		total = size / 100 + 1
		session = setupSession()
		for i in range(total):
			time.sleep(0.01)
			
			iterator = i * 100
			url = r"https://www.google.com/search?q={word}&newwindow=1&biw=300&bih=629&tbm=isch&ijn={times}&start={start}"
			try:
				browser.get(url.format(word=wordSearch, start=iterator,times = i))

			except httplib.BadStatusLine:
				pass
			except SocketError as e:
				if e.errno != errno.ECONNRESET:
					raise # Not error we are looking for
				pass
		time.sleep(2)
		for i in range(total):
			iterator = i * 100
			filename = os.path.join("results", word +".txt")
			newName = word + '_' + str(i) +'.txt'
			browser = webdriver.Chrome()
			print url.format(word=word, start=iterator,times = i)
			filepath = '/home/hwang3/Downloads'
			if i == 0:
				if "f.txt" in os.listdir(filepath):
					print "change name to be " + newName
					os.rename(os.path.join(filepath,'f.txt'), os.path.join(filepath,newName))
			else:
				fileSpecial = "f ("+str(i)+").txt"
				if fileSpecial in os.listdir(filepath):
					print "change name to be " + newName
					os.rename(os.path.join(filepath,fileSpecial), os.path.join(filepath,newName))
				else: 
					print "fail to find the file"
			#Note here we may use linux version of the downloads page and assume the default downloads
			#and you may change the filepath to be the default path of the Chrome downloads
			try:
				with open(os.path.join(filepath,newName),'r') as myfile:
					file1 = myfile.read()
				results = re.findall(r'<img data-src="(.+?)"',file1)
				process = multiprocessing.Pool(50)
				process.map(multiPara_wrapper,zip(results, [self.word] * len(results)))
			except IOError:
				print ("can not find the file called:" + str(newName) + "and it may be caused by the bad connection or bad file got from server")

			# with open(filename, 'a') as f:
			# 	for g in results:
			# 		f.write(str(g)+"\n")
			# 	f.write("\n"+str(i)+"\n")
def makeFolder(word):
	# if not os.path.join(sys.path[0], 'results'):
	folderPath = os.path.join(sys.path[0], 'results')
	try:

		if not os.path.exists(os.path.join(folderPath ,word)):
			os.mkdir(os.path.join(folderPath ,word))
	except OSError , e:
		if e.errno != 17:
			raise
		else:
			pass
	return os.path.join(folderPath ,word)


def _download(url,word):
	imgUrl = url
	session = setupSession()
	# try:
	image = session.get(imgUrl,timeout = 15)
	index = random.randint(0,999)
	folderName = makeFolder(word)
	with open(os.path.join(folderName,str(index) ),'wb') as fout:
		fout.write(image.content)
	# except Exception as e:
	# 	print ("failed to download one pages with url of " + str(url))

def readFile(filename):
	_list=[]
	with open (filename, 'r') as fin:
		line = fin.readline()
		while line:
			_list.append(str(line).rstrip())
			line = fin.readline()
	return _list

if __name__ == '__main__':
	start = time.time()
	display = Display(visible=0, size=(1024, 768))
	display.start()
	nameList = readFile('testlist.txt')
	browser = webdriver.Chrome()
	for i in nameList:

		GoogleDownloader(word = i, size = 10, browser = browser)

	browser.close()
	end = time.time()
	display.stop()
	print (end - start)

#https://www.google.com/search?q=hsbc&newwindow=1&biw=677&bih=629&tbm=isch&ijn=1&start=100
