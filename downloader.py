import multiprocessing
import requests
import imghdr
import os

def _setupSession():
	session = requests.Session()
	session.header = { 'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0","Accept-Encoding": "gzip, deflate, sdch"}
	return session


# function to get one image specified with one url
def _download(url, imageName, folderName):
	session = _setupSession()
	try:
		# time out is another parameter tuned
		# fit for the network about 10Mb
		image = session.get(url, timeout = 5)
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

# wrapper for map function
def multiPara_wrapper(args):
	return _download(*args)


class ImageDownloader():
	def __init__(self, size = 100, timeout = 5):
		self.processPool = multiprocessing.Pool(size)
		self._timeout = timeout
	

	def download(self, url_name_tuple, folderName):
		urlList = list(map(lambda x: x[0], url_name_tuple))
		nameList = list(map(lambda x: str(x[1]), url_name_tuple))
		self.processPool.map(multiPara_wrapper,
								zip(urlList, nameList, [folderName] * len(urlList)))


if __name__ == '__main__':
	downloader = ImageDownloader(size=1)
	url_name_tuple = ("http://android-wallpapers.25pp.com//fs08/2016/10/12/0/2000_3f2bef2275508ed9873050a93caf717d_900x675.jpg",'test')
	downloader.download([url_name_tuple], 'results')