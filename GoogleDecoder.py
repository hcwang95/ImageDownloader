# this is the google tester to get a the txt file and to find the url

import os
from selenium import webdriver


# chromedriver = 'C:\Users\hwang3\Downloads'
# os.environ["webdriver.chrome.driver"] = chromedriver
driver = webdriver.Chrome()
driver.get("http://stackoverflow.com")
driver.quit()
