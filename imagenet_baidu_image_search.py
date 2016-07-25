#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: loveNight
# @Date:   2015-10-28 19:59:24
# @Last Modified by:   loveNight
# @Last Modified time: 2015-11-15 19:24:57


import urllib
import requests
import os
import re
import sys
import time
import threading
from datetime import datetime as dt
from multiprocessing.dummy import Pool
from multiprocessing import Queue

class BaiduImgDownloader(object):

    str_table = {
        '_z2C$q': ':',
        '_z&e3B': '.',
        'AzdH3F': '/'
    }

    char_table = {
        'w': 'a',
        'k': 'b',
        'v': 'c',
        '1': 'd',
        'j': 'e',
        'u': 'f',
        '2': 'g',
        'i': 'h',
        't': 'i',
        '3': 'j',
        'h': 'k',
        's': 'l',
        '4': 'm',
        'g': 'n',
        '5': 'o',
        'r': 'p',
        'q': 'q',
        '6': 'r',
        'f': 's',
        'p': 't',
        '7': 'u',
        'e': 'v',
        'o': 'w',
        '8': '1',
        'd': '2',
        'n': '3',
        '9': '4',
        'c': '5',
        'm': '6',
        '0': '7',
        'b': '8',
        'l': '9',
        'a': '0'
    }

    re_objURL = re.compile(r'"objURL":"(.*?)".*?"type":"(.*?)"')
    re_downNum = re.compile(r"download \s(\d+)\s images")
    headers = {
        'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
        "Accept-Encoding": "gzip, deflate, sdch",
    }

    def __init__(self, word, dirpath=None, processNum=30):
        #if " " in word:
            #raise AttributeError("This Script Only Support Single Keyword!")
        self.word = word
        self.char_table = {ord(key): ord(value)
                           for key, value in BaiduImgDownloader.char_table.items()}
        if not dirpath:
            dirpath = os.path.join(sys.path[0], 'results')
        self.dirpath = dirpath
        self.jsonUrlFile = os.path.join(sys.path[0], 'jsonUrl.txt')
        self.logFile = os.path.join(sys.path[0], 'logInfo.txt')
        self.errorFile = os.path.join(sys.path[0], 'errorUrl.txt')
        if os.path.exists(self.errorFile):
            os.remove(self.errorFile)
        if not os.path.exists(self.dirpath):
            os.mkdir(self.dirpath)
        self.pool = Pool(30)
        self.session = requests.Session()
        self.session.headers = BaiduImgDownloader.headers
        self.queue = Queue()
        self.messageQueue = Queue()
        self.index = 0
        self.promptNum = 10
        self.lock = threading.Lock()
        self.delay = 1.5
        self.QUIT = "QUIT"
        self.printPrefix = "**"
        self.processNum = processNum

    def start(self):

        t = threading.Thread(target=self.__log)
        t.setDaemon(True)
        t.start()
        self.messageQueue.put(self.printPrefix + "Scripits Run")
        print (self.printPrefix + "Scripits Run")
        start_time = dt.now()
        urls = self.__buildUrls()
        self.messageQueue.put(self.printPrefix + "Get %s Json Request" % len(urls))
        print (self.printPrefix + "Get %s Json Request" % len(urls))
        self.pool.map(self.__resolveImgUrl, urls)
        while self.queue.qsize():
            imgs = self.queue.get()
            print(imgs)
            self.pool.map_async(self.__downImg, imgs)
        self.pool.close()
        self.pool.join()
        self.messageQueue.put(self.printPrefix + "Downloaded! %s images,totally used up %s" %
                              (self.index, dt.now() - start_time))
        self.messageQueue.put(self.printPrefix + "Please go to %s check the results!" % self.dirpath)
        self.messageQueue.put(self.printPrefix + "Error Message Stored at %s" % self.errorFile)
        self.messageQueue.put(self.QUIT)
        print (self.printPrefix + "Downloaded! %s images,totally used up %s" %
                              (self.index, dt.now() - start_time))
        print (self.printPrefix + "Please go to %s check the results!" % self.dirpath)
        print (self.printPrefix + "Error Message Stored at %s" % self.errorFile)
        print (self.QUIT)

    def __log(self):

        with open(self.logFile, "w"''', encoding = "utf-8"''') as f:
            while True:
                message = self.messageQueue.get()
                if message == self.QUIT:
                    break
                message = str(dt.now()) + " " + message
                if self.printPrefix  in message:
                    print(message)
                elif "Downloaded" in message:
                    downNum = self.re_downNum.findall(message)
                    if downNum and int(downNum[0]) % self.promptNum == 0:
                        print(message)
                f.write(message + '\n')
                f.flush()

    def __getIndex(self):
        self.lock.acquire()
        try:
            return self.index
        finally:
            self.index += 1
            self.lock.release()

    def decode(self, url):

        for key, value in self.str_table.items():
            url = url.replace(key, value)
        return url.translate(self.char_table)

    def __buildUrls(self):

        word = self.word[0]
        if len(self.word) > 1:
            for dw in self.word[1:len(self.word)]:
                word += "+" + dw
        url = r"http://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&ct=201326592&fp=result&queryWord={word}&cl=2&lm=-1&ie=utf-8&oe=utf-8&st=-1&ic=0&word={word}&face=0&istype=2nc=1&pn={pn}&rn=60"
        time.sleep(self.delay)
        html = self.session.get(url.format(word=word, pn=0), timeout = 15).content.decode('utf-8')
        results = re.findall(r'"displayNum":(\d+),', html)
        #maxNum = int(results[0]) if results else 0
        maxNum = self.processNum
        urls = [url.format(word=word, pn=x)
                for x in range(0, maxNum + 1, 60)]
        with open(self.jsonUrlFile, "w" ''',encoding="utf-8"''') as f:
            for url in urls:
                f.write(url + "\n")

        return urls

    def __resolveImgUrl(self, url):

        time.sleep(self.delay)
        html = self.session.get(url, timeout = 15).content.decode('utf-8')

        datas = self.re_objURL.findall(html)
        print(datas)
        imgs = [Image(self.decode(x[0]), x[1]) for x in datas]

        self.messageQueue.put(self.printPrefix + "Extract %s images url path" % len(imgs))
        self.queue.put(imgs)

    def __downImg(self, img):

        imgUrl = img.url
        print()
        try:
            time.sleep(self.delay)
            res = self.session.get(imgUrl, timeout = 15)
            message = None
            if str(res.status_code)[0] == "4":
                message = "\n%s: %s" % (res.status_code, imgUrl)
            elif "text/html" in res.headers["Content-Type"]:
                message = "\nCannot Open File: %s" % imgUrl
        except Exception as e:
            message = "\nException: %s\n%s" % (imgUrl, str(e))
        finally:
            if message:
                self.messageQueue.put(message)
                self.__saveError(message)
                return
        index = self.__getIndex()

        self.messageQueue.put("Download %s images:%s" % (index + 1, imgUrl))
        filename = os.path.join(self.dirpath, str(index) + "." + img.type)
        with open(filename, "wb") as f:
            f.write(res.content)

    def __saveError(self, message):
        self.lock.acquire()
        try:
            with open(self.errorFile, "a"''', encoding="utf-8"''') as f:
                f.write(message)
        finally:
            self.lock.release()


class Image(object):

    def __init__(self, url, type):
        super(Image, self).__init__()
        self.url = url
        self.type = type


if __name__ == '__main__':
    print("Welcome to use the Baidu Image Search Download Service!\n Only a single word query is supported!")
    print("Results saved in results folder")
    print("=" * 50)

    synset = open("synset_words.txt")
    line = synset.readline()

    while line:
        #
        words = line.split(",")
        print(words)
        species = words[0].split(" ")
        category = species[0]
        #
        if len(species) < 2:
            print("Error Synset Words!")
            exit(1)
        else:
            subcategory = species[1:len(species)]
            filepath = "results/" + subcategory[0]
            if len(subcategory) > 1:
                for pt in subcategory[1:len(subcategory)]:
                    filepath += "_" + pt
            print(words)
            print(subcategory)
            print(filepath)
            down = BaiduImgDownloader(subcategory, filepath, 5)
            down.start()
        #
        if len(words) > 1:
            for word in words[1:len(words)]:
                subcate = word.split(" ")
                subcategory = subcate[1:len(subcate)]
                filepath = "results/" + subcategory[0]
                if len(subcategory) > 1:
                    for pt in subcategory[1:len(subcategory)]:
                        filepath += "_" + pt
                print(words)
                print(subcategory)
                print(filepath)
                down = BaiduImgDownloader(subcategory, filepath, 5)
                down.start()
        #
        line = synset.readline()
