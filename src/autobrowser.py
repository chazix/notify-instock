import asyncio
import logging
import platform
import os

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.remote_connection import LOGGER

from csvCustom import CCsvOutputData

class CAutoBrowser:
    def __init__(self, name, url):
        # the name of the site
        self.m_name = name
        # the root url of the site, starts here
        self.m_url  = url

    def BeginScrapeThread(self, q):
        raise NotImplementedError()

    async def BeginScrape(self, q):
        raise NotImplementedError()

    async def DoAutomation(self, args=[], queries=[]):
        raise NotImplementedError()

class CAutoBrowserCsvScrape(CAutoBrowser):
    def __init__(self, name, url, queries):
        # change logging to prevent spam for selenium
        LOGGER.setLevel(logging.WARNING)

        # the name of the site
        self.m_name = name
        # the root url of the site, starts here
        self.m_url  = url
        self.driver = {q:None for q in queries}

    def CsvHeader(self):
        return NotImplementedError()

    def WriteCsvData(self, q, data, outdir, extrapath='', spacing=0):
        pageCsvData = CCsvOutputData([q], self.m_name, self.m_url, self.CsvHeader())
        pageCsvData.AddData(q, data)
        pageCsvData.WriteCsvFile(outdir, extrapath=extrapath, spacing=spacing)

    def RestoreCsvData(self, restoreDir, outdata, toFind='', args=[]):
        if os.path.exists(restoreDir):
            # find all prior paged csv in directory, up to curPage-1 on this date
            valid  = []
            for csv in os.listdir(restoreDir):
                if toFind in csv and self.ValidRestoreCondition(csv, args):
                    valid.append('{0}/{1}'.format(restoreDir, csv))
            for csv in valid:
                with open(csv, 'r') as f:
                    # we don't want to parse an empty file
                    if os.stat(csv).st_size == 0:
                        continue
                    next(f) # ignore first line csv header
                    for line in f:
                        line = line.strip()
                        data = line.split(';')
                        self.ProcessRestoredCsvData(csv, data, outdata)

    def ProcessRestoredCsvData(self, path, data, outdata):
        return NotImplementedError()

    def ValidRestoreCondition(self, path, args=[]):
        return NotImplementedError()

    def CreateBrowserForPlatform(self, q, chromeOptions):
        if self.driver[q] is None:
            osType = platform.system()
            if osType == 'Windows':
                self.driver[q] = webdriver.Chrome(executable_path='./chromedriver_win32/chromedriver.exe', options=chromeOptions)
            elif osType == 'Linux':
                self.driver[q] = webdriver.Chrome(executable_path='./chromedriver_linux64/chromedriver', options=chromeOptions)
            elif osType == 'Darwin':
                self.driver[q] = webdriver.Chrome(executable_path='./chromedriver_mac64/chromedriver', options=chromeOptions)

    def OpenBrowserForCaptcha(self, q, getUrl, successClassElement):
        # have to close browser in-case we're headless, and one is running already
        self.CloseBrowser(q)
        if self.driver[q] is None:
            chromeOptions = webdriver.ChromeOptions()
            chromeOptions.add_argument('--incognito')
            self.CreateBrowserForPlatform(q, chromeOptions)
            self.driver[q].implicitly_wait(30)
            # only need to do get request if driver is null, should already be loaded there due to the redirect
            self.driver[q].get(getUrl)
        try:
            # wait up to ten minutes
            WebDriverWait(self.driver[q], 600).until(
                EC.presence_of_element_located((By.CLASS_NAME, successClassElement))
            )
        finally:
            self.CloseBrowser(q)

    def OpenBrowserForSource(self, q, getUrl, quitOnLoad=True):
        if self.driver[q] is None:
            chromeOptions = webdriver.ChromeOptions()
            chromeOptions.add_argument('--incognito')
            chromeOptions.add_argument('--log-level=3')
            chromeOptions.set_headless()
            self.CreateBrowserForPlatform(q, chromeOptions)
            self.driver[q].implicitly_wait(30)
        self.driver[q].get(getUrl)
        pageSource = self.driver[q].page_source
        if quitOnLoad:
            self.CloseBrowser(q)
        return pageSource

    def ScrollBrowserToElement(self, q, element):
        if self.driver[q] is not None:
            ActionChains(self.driver[q]).move_to_element(element).perform()

    def CloseBrowser(self, q):
        if self.driver[q] is not None:
            self.driver[q].quit()
            self.driver[q] = None

    async def DoAutomation(self, args=[], queries=[]):
        csvHeader = self.CsvHeader()
        csvData   = CCsvOutputData(queries, self.m_name, self.m_url, csvHeader)
        tasks     = []

        for q in queries:
            tasks.append(asyncio.create_task(self.BeginScrape(q)))

        for t in tasks:
            await t
            # needs to always have searchTerm
            # data => (searchTerm, ...)
            data = t.result()
            for d in data:
                csvData.AddData(data[0], d)
        args.append(csvData)