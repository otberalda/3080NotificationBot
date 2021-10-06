from bs4 import BeautifulSoup
import pandas as pd
import time
import requests
import telegram_send as ts


def checkBestBuyStock(page):
    soup = BeautifulSoup(page.content, features="html.parser")
    items = soup.find(id="main-results")

    itemsProcessed = []

    for item in items.findAll("li"):
        row_processed = []
        itemTitle = item.find("h4", {"class": "sku-header"})
        itemAvailability = item.find("div", {"style": "position:relative"})

        status = "Available"

        if itemAvailability and (itemAvailability.text == "Sold Out" or itemAvailability.text == "Coming Soon" or
                                 itemAvailability.text == "In Store Only"):
            status = "Sold Out"

        if itemTitle:
            row_processed.append(itemTitle.text)
            row_processed.append(status)
        if row_processed:
            itemsProcessed.append(row_processed)

    df = pd.DataFrame.from_records(itemsProcessed, columns=["Item Title", "Status"])
    return df


def checkNeweggStock(page):
    soup = BeautifulSoup(page.content, features="html.parser")
    items = soup.find("div", {"class": "items-grid-view"})

    items_processed = []

    for row in items.findAll("div", {"class": "item-cell"}):
        row_processed = []
        itemTitle = row.find("a", {"class": "item-title"})
        itemPromoText = row.find("p", {"class": "item-promo"})
        itemPrice = row.find("li", {"class": "price-current"})
        intPrice = ""
        nums = ["1234567890"]
        for i in itemPrice.text:
            if i in nums[0]:
                intPrice += i
        print(int(intPrice))

        status = "Available"

        if itemPromoText and itemPromoText.text == "OUT OF STOCK":
            status = "Sold Out"

        if itemTitle:
            row_processed.append(itemTitle.text)
            row_processed.append(status)

        if row_processed:
            items_processed.append(row_processed)

    df = pd.DataFrame.from_records(items_processed, columns=["Item Title", "Status"])

    return df


if __name__ == '__main__':
    for i in range(10000000):
        print("Main line start")
        # search for RTX 3000 series
        NEWEGG3080s = 'https://www.newegg.com/p/pl?N=100007709%20601357247'
        BESTBUY3080s = 'https://www.bestbuy.com/site/searchpage.jsp?st=nvidia+3080&_dyncharset=UTF-8&_dynSessConf=&id' \
                       '=pcat17071&type=page&sc=Global&cp=1&nrp=&sp=&qp=&list=n&af=true&iht=y&usc=All+Categories&ks' \
                       '=960&keys=keys'
        BESTBUY_URLS = [BESTBUY3080s]
        NEWEGG_URLS = [NEWEGG3080s]

        for url in NEWEGG_URLS:
            headers = {'User-Agent': 'test'}
            page = requests.get(url, headers=headers)
            stock_df = checkNeweggStock(page)
            print(stock_df)
            if "Available" in stock_df.Status.values:
                indexes = []
                print("Stock Available!")
                for i in range(len(stock_df.values)):
                    if stock_df.values[i][1] == 'Available':
                        indexes.append(i)
                        print(stock_df.values[i][0])

                for x in indexes:
                    title = stock_df.values[x][0].replace(" ", "+")
                    ts.send(messages=['https://www.newegg.com/p/pl?d=' + title[:70]])
            else:
                print("Everything out of stock!")
            time.sleep(5)

        for url in BESTBUY_URLS:
            headers = {'User-Agent': 'test'}
            page = requests.get(url, headers=headers)
            stock_df = checkBestBuyStock(page)
            print(stock_df)
            if "Available" in stock_df.Status.values:
                indexes = []
                print("Stock Available!")
                for i in range(len(stock_df.values)):
                    if stock_df.values[i][1] == 'Available':
                        indexes.append(i)
                        print(stock_df.values[i][0])

                for x in indexes:
                    title = stock_df.values[x][0].replace(" ", "+")
                    ts.send(messages=['https://www.bestbuy.com/site/searchpage.jsp?st=' + title[:50]])
            else:
                print("Everything out of stock!")
            time.sleep(5)
        print("Main line end")
        print(i)
