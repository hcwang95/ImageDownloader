Google Image Downloader
===========================
[![Build Status](https://travis-ci.org/whcacademy/imageDownloader.svg?branch=master)](https://travis-ci.org/whcacademy/imageDownloader)

A image crawler driving Google Chrome to download images from Google Image.


## Getting Started For the Windows version

### Dependency:
    python3 or python2
    google chrome on Windows
    python package: selenium requests

## Execute
### Prepare your ID:
Store your target id in one file with a name, say 'id.txt'. The sample content is shown below

#### Sample content of id.txt
    apple
    banana
    ...

Then execute the downloader by
```
python googleForWindows.py --fileName [fileroot]\id.txt --root testResult --size 100
```

After running, all results will be in 'testResults' folder, with one folder per id and ideal size of images is 100.
### Note:
1. The verison of chrome driver may not fit for chrome version, please check your chrome version and download corresponding driver from [here](https://sites.google.com/a/chromium.org/chromedriver/downloads)
2. The number of output images may not be equal to the size option since there could be some invalid url
