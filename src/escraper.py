import argparse
import asyncio
from datetime import datetime as dt
from newegg import CNewEggScrape

def ParseArgs():
    args = argparse.ArgumentParser(description='Scrapes through eCommerce sites and collects product information')
    args.add_argument('-s', '--search', nargs='+', help='Search terms to use when scraping the specified eCommerce sites', required=True)
    args.add_argument('-ne', '--newegg', action='store_true', help='Scrapes through NewEgg notifying when items available')
    args.add_argument('-sp', '--startpage', default=None, help='The page in the search to start at')
    args.add_argument('-aq', '--additionalQuery', nargs='+', help='Additional query parameters to append onto the search url')
    return args.parse_args()

def ExecuteSiteAutomation(loop, site, queries):
    print('Beginning Search of {0} for: {1}'.format(site.m_name, queries))
    outSiteData = []
    loop.run_until_complete(site.DoAutomation(outSiteData, queries))
    # line separation between next site
    print()

if __name__ == '__main__':
    args    = ParseArgs()
    queries = args.search

    if len(queries) > 0:
        autoBrowsers = []
        if args.newegg:
            autoBrowsers.append(CNewEggScrape('NewEgg', 'https://www.newegg.com', queries, startPage=args.startpage, filterQueries=args.additionalQuery))

        if not autoBrowsers:
            print('No sites specified - run script with --help')
            exit(1)

        loop = asyncio.get_event_loop()
        for site in autoBrowsers:
            ExecuteSiteAutomation(loop, site, queries)
