import asyncio
import aiohttp
import webbrowser
import random

from bs4 import BeautifulSoup

from autobrowser import CAutoBrowserCsvScrape
from product import CProduct
from product import CProductPage

class CNewEggScrape(CAutoBrowserCsvScrape):
    def __init__(self, name, url, queries, startPage=None, filterQueries=None):
        super().__init__(name, url, queries)
        try:
            self.m_startPage = None if startPage is None else int(startPage)
            self.m_filterQueries = filterQueries
        except:
            print('  {0}: Invalid Start Page Specified: {1} - Defaulting to page 1'.format(name, startPage))
            self.m_startPage = None

    def SearchQuery(self, item, page=None):
        search = 'p/pl?d={0}'.format(item)
        if page is not None:
            search = 'p/pl?d={0}&page={1}'.format(item, page)
        if self.m_filterQueries is not None:
            search = search + search.join(self.m_filterQueries)
        return search

    async def DoAutomation(self, args=[], queries=[]):
        tasks = []
        for q in queries:
            tasks.append(asyncio.create_task(self.BeginScrape(q, cpage=self.m_startPage)))

        tasksComplete = False
        while not tasksComplete:
            t = tasks.pop(0)
            await t
            await asyncio.sleep(60)
            # we want this one to run until we have a successful purchase we could make
            tasks.append(asyncio.create_task(self.BeginScrape(q, cpage=self.m_startPage)))

    # this is used as a notifier for when a product becomes available
    async def BeginScrape(self, q, cpage=None, tpage=None):
        # need a user-agent, else we get a 403 for the webrequest
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            needsPages = True
            curPage    = cpage
            totalPages = tpage
            pages      = []

            while True:
                getUrl = self.m_url + '/{0}'.format(self.SearchQuery(q, curPage))
                async with session.get(getUrl, headers=headers) as resp:
                    searchResp = await resp.text()
                    soup = BeautifulSoup(searchResp, 'html.parser')
                    page = CProductPage(curPage)

                    captcha = "are you a human" in soup.find('title').contents[0].strip().lower()
                    if captcha:
                        print('  {0}: [{1}] - Page: {2}/{3} - Captcha Detected'.format(self.m_name, q, '1' if curPage == None else curPage, '?' if totalPages == None else totalPages))
                        # let's solve the captcha manually
                        self.OpenBrowserForCaptcha(q, getUrl, 'item-cell')
                        continue

                    # first page, we need to find the total pages for this query
                    if needsPages == True:
                        curPage    = 1 if curPage == None else curPage
                        totalPages = soup.find('span', {'class':'list-tool-pagination-text'}).find('strong')
                        if totalPages is not None:
                            totalPages = int(totalPages.contents[-1].strip())
                        else:
                            totalPages = 1
                        page.m_page = curPage
                        needsPages  = False

                    # can early out, such as if a startpage was requested, but there isn't results at this page
                    if curPage > totalPages:
                        print('  {0}: Invalid Start Page [{1} > {2}]'.format(self.m_name, curPage, totalPages))
                        print('  {0}: [{1}]'.format(self.m_name, q))
                        print('    Found: 0 Products')
                        break
                    pages.append(page)

                    print('  {0}: [{1}] - Page: {2}/{3}'.format(self.m_name, q, curPage, totalPages))
                    elementsRoot = soup.find('div', {'class':'list-wrap'})
                    productElements = elementsRoot.find_all('div', {'class':'item-container'})
                    print('    Found: {0} Products'.format(len(productElements)))
                    for p in productElements:
                        aTagElement = p.find('a', {'class':'item-img'})
                        producturl  = aTagElement['href']
                        name        = aTagElement.find('img')['title']
                        image       = aTagElement.find('img')['src']
                        image = ('https:' + image) if not image.startswith('https:') else image

                        priceElement = p.find('ul', {'class':'price'})
                        hasPrice = 'is-price-coming-soon' not in priceElement['class']
                        price = 'COMING SOON'
                        if hasPrice:
                            price = p.find('li', {'class':'price-current'})
                            hasPriceElement = price.find('strong') is not None and price.find('sup') is not None
                            if (hasPriceElement):
                                price = price.find('strong').contents[0] + price.find('sup').contents[0]
                            else:
                                price = "???"

                        canPurchase = False
                        buttonElement = p.find('div', {'class':'item-button-area'})
                        if buttonElement is not None:
                            hasButton = buttonElement.find('button') is not None
                            if hasButton:
                                canPurchase = 'add to cart' in buttonElement.find('button').contents[0].strip().lower()

                        if canPurchase:
                            print('    {0} - {1} !PURCHASEABLE!'.format(price, name))
                            webbrowser.open(getUrl)
                            webbrowser.open(producturl)
                            exit(1)

                        product = CProduct(rooturl=self.m_url, name=name, category=q, price=price, desc='', purl=producturl, iurl=image)
                        page.AddProduct(product)

                    page.SetSuccess()
                    curPage += 1
                    if curPage > totalPages:
                        break
                    await asyncio.sleep(random.randint(2, 5))

            return (q, pages)