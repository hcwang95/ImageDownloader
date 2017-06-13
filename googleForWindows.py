import urllib
import requests
import os
import re
import time
from selenium import webdriver
import multiprocessing
import random
import sys
from socket import error as SocketError
import errno
import argparse
import imghdr
import uuid
import csv

# wrapper for map function
def multiPara_wrapper(args):
	return _download(*args)

# use selenium to get the list of URLs
def openBrowserRecursively(total, idName, browser):
	try:
		for i in range(total):
			iterator = i * 100
			url = r"https://www.google.com/search?q={word}&newwindow=1&biw=300&bih=629&tbm=isch&ijn={times}&start={start}"
			try:
				browser.get(url.format(word= idName, start=iterator,times = i))
			except SocketError as e:
				if e.errno != errno.ECONNRESET:
					raise # raise to reset the connection
				pass
		time.sleep(1.5) # 1.5 seconds is the tuned time for HKU service not to be monitored and closed
	except:
		os.system("taskkill /im chorme.exe /F")
		openBrowserRecursively(total, idName, browser)
	
# basic session setup
def setupSession():
	session = requests.Session()
	session.header = { 'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0","Accept-Encoding": "gzip, deflate, sdch"}
	return session


class GoogleDownloader():
	def __init__(self, nameList, root, size, process, browser):
		assert browser != None, "drive cannot be  None!"
		self.process = process
		self.browser = browser
		self.nameList = nameList
		self.size = size
		self.root = root

	# main crawling start
	def run(self):
		for i in nameList:
			self.oneID(i)

	def oneID(self, name):
		wordSearch = ''
		subcategory = name.split(' ')
		name = name.replace(' ', '_')
		wordSearch = subcategory[0]
		if len(subcategory[1:]) >= 1:
			for pt in subcategory[1:]:
				wordSearch += "+" + pt
		print (wordSearch)
		total = int(self.size / 100)
		
		openBrowserRecursively(total, wordSearch, self.browser)
		# after trigger getting the file list, then the file will be
		# download but name with f.txt
		try:
			for i in range(total):
				iterator = i * 100
				filename = os.path.join("results", name +".txt")
				newName = name + '_' + str(i) +'.txt'

				# here is the hardcode part
				# one may change to his or her own default downloading folder
				filepath = 'C:\\Users\\hwang3\\Downloads'

				if i == 0:
					if "f.txt" in os.listdir(filepath):
						print ("change name to be " , newName)
						os.rename(os.path.join(filepath,'f.txt'), os.path.join(filepath,newName))
				else:
					fileSpecial = "f (%d).txt" % i
					if fileSpecial in os.listdir(filepath):
						print ("change name to be " , newName)
						os.rename(os.path.join(filepath,fileSpecial), os.path.join(filepath,newName))
					else:
						print ("fail to find the file")
		except:
			print("something bad happen, maybe encountering some repeated names")
			os.remove('C:\\Users\\hwang3\\Downloads\\f.txt')
			return

		# after rename and locate the url list, then we conduct the final crawling part
		indexList = [i for i in range(1, 101)]
		# try:
		folderName = self.makeFolder(name)
		for i in range(total):
			newName = name + '_' + str(i) +'.txt'
			with open(os.path.join(filepath,newName),'r') as myfile:
				file1 = myfile.read()
			results = re.findall(r'"ou":"(.+?)"',file1)
			self.dump_imInfo(folderName, results)
			self.process.map(multiPara_wrapper,
							zip(results, [folderName] * len(results), indexList[:len(results)]))
				
		# except IOError:
		# 	print ("can not find the file called:" + str(newName) + "and it may be caused by the bad connection or bad file got from server")

	def makeFolder(self, fileName):
		try:
			if not os.path.exists(os.path.join(self.root, fileName)):
				os.mkdir(os.path.join(self.root, fileName))
			else:
				print('duplicated root name')
		except OSError as e:
			if e.errno != 17:
				raise
			else:
				pass
		return os.path.join(self.root, fileName)

	def dump_imInfo(self, folderName, results):
		with open(os.path.join(folderName, 'imInfo.csv'), 'w', newline='') as csvfile:
			writer = csv.writer(csvfile, delimiter=',')
			writer.writerow(['img_name', 'uuid', 'url'])
			for url in results:
				writer.writerow([str(results.index(url)+1),str(uuid.uuid4().hex),str(url)])
# function to get one image specified with one url
def _download(url, folderName, index):
	imgUrl = url
	session = setupSession()
	try:
		# time out is another parameter tuned
		# fit for the network about 10Mb
		image = session.get(imgUrl, timeout = 5)
		imageName = str(index)
		with open(os.path.join(folderName, imageName),'wb') as fout:
			fout.write(image.content)
		fileExtension = imghdr.what(os.path.join(folderName, imageName))
		if fileExtension is None:
			os.remove(os.path.join(folderName, imageName))
		else:
			newName = imageName + '.' + str(fileExtension)
			os.rename(os.path.join(folderName, imageName), os.path.join(folderName, newName))

	except Exception as e:
		print ("failed to download one pages with url of " + str(url))

# basic funciton to get id list
def readFile(filename):
	_list=[]
	with open (filename, 'r') as fin:
		line = fin.readline()
		while line:
			_list.append(str(line).rstrip())
			line = fin.readline()
	return _list


def arg_parse():
	parser = argparse.ArgumentParser(description='Argument Parser for google image downloader')
	parser.add_argument('--root', help='output file root', 
							default='results', type=str)
	parser.add_argument('--fileName', help='the name of the file which constain the id', 
							default='testlist.txt', type=str)
	parser.add_argument('--size', help='number of image per id', 
							default=100, type=int)
	parser.add_argument('--process', help='number of process in parallel', 
							default=100, type=int)
	args = parser.parse_args()
	return args


if __name__ == '__main__':
	args = arg_parse()
	start = time.time()
	assert args.fileName != None, "Name list cannot be None!"
	nameList = readFile(args.fileName)
	processPool = multiprocessing.Pool(args.process)
	browser = webdriver.Chrome()
	downloader = GoogleDownloader(nameList = nameList, root = args.root, size = args.size, 
									process = processPool, browser = browser)
	downloader.run()
	end = time.time()
	browser.close()
	print ('task end, time consumed:', end - start, 'seconds')
