Google Image Downloader
===========================
[![Build Status](https://travis-ci.org/whcacademy/imageDownloader.svg?branch=master)](https://travis-ci.org/whcacademy/imageDownloader)

A image crawler driving Google Chrome to download images from Google Image.


## Getting Started

### Dependency:
    python3 or python2
    google chrome on Windows
    python package: selenium requests
    Proper chrome driver of selenium
Please follow the sequence to adapt selenium:
Google Chrome Version -> Selenium Version -> Selenium Google Driver

Then install the dependency by
```
pip install -r requirements.txt
```

### Execute
#### Prepare your ID:
Store your target id in one file with a name, say 'id.txt'. The sample content is shown below

##### Sample content of id.txt
    apple
    banana
    ...

Then execute the downloader by (For windows and Linux)
```
python googleImageDownload.py --filename [fileroot]\id.txt --root testResult --size 100 
```


One can get the argument by
```
python googleImageDownload.py --help
```

After running, all results will be in 'testResults' folder, with one folder per id and ideal size of images is 100.

### Note:
1. The verison of chrome driver may not fit for chrome version, please check your chrome version and download corresponding driver from [here](https://sites.google.com/a/chromium.org/chromedriver/downloads)
2. The number of output images may not be equal to the size option since there could be some invalid url
3. There are some important number to customize for your better experience, please check googleForWindows.py to adapt it.
