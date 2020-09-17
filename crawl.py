import re
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import urlparse, urljoin
import urllib.error
import numpy as np
import validators
import json
import time
import os
from datetime import datetime
import sys


requests.packages.urllib3.disable_warnings()

# Function to check the given url is valid or not
def url_validation(url):
    validationStatus = validators.url(url)
    return validationStatus

# Function to fetch internal, external asset and links from the given url
def fetch(url):

    headers = {"Content-Type":"application/json", "Accept":"application/json"}
    response = requests.get(url, headers=headers, verify=False)
    htmlParseObject = BeautifulSoup(response.text, 'html.parser')
    domainName = urlparse(url).netloc
    parsedHref = urlparse(url)


    externalAsset = []
    internalAssetRaw = []
    internalAssetComplete = []
    links = []
    assetslinks = {}

    for imgTag in htmlParseObject.findAll('img'):
        imgSrc = imgTag.get('src')
        if domainName not in imgSrc and re.match('^http', imgSrc):
            externalAsset.append(imgSrc)
        if domainName  in imgSrc:
            internalAssetComplete.append(imgSrc)
        if domainName not in imgSrc and not re.match('^http', imgSrc):
            filePath = parsedHref.scheme + "://" + parsedHref.netloc + "/" + imgSrc
            internalAssetRaw.append(imgSrc)
            internalAssetComplete.append(filePath)

    for link in htmlParseObject.find_all(attrs={'href': re.compile("http")}):
        hyperLink = link.get('href')
        if not url_validation(hyperLink):
            continue
        links.append(hyperLink)
    
    assetslinks["externalAsset"] = externalAsset
    assetslinks["internalAssetRaw"] = internalAssetRaw
    assetslinks["internalAssetComplete"] = internalAssetComplete
    assetslinks["Links"] = links

    return assetslinks
    
# Function to crawl through the site and fetch internal and external asset and links from the each url/html page
def getWebsiteAssets(url):

    urls = set()
    intUrls = set()
    extUrls = set()
    assetslinksdata = {}
    domainName = urlparse(url).netloc
    assetslinksdata["domainName"] = domainName
    htmlParseObject = BeautifulSoup(requests.get(url).content, "html.parser")
    for anchorTag in htmlParseObject.findAll("a"):
        hyperLink = anchorTag.attrs.get("href")
    
        if hyperLink == "" or hyperLink is None:
            continue

        hyperLink = urljoin(url, hyperLink)

        if not url_validation(hyperLink):
            continue
        if hyperLink in intUrls:
            continue
        if domainName not in hyperLink:
            if hyperLink not in extUrls:
                extUrls.add(hyperLink)
            continue

        urls.add(hyperLink)
        intUrls.add(hyperLink)
    
    for urls in intUrls:
        assetslinksdata[urls] = fetch(urls)
    
    return assetslinksdata

# Function to check list is empty or not
def Enquiry(listVar): 
    if not listVar: 
        return 1
    else: 
        return 0

# Function to download assets
def webassetsDownload(url, path, domainName):

    path = path + "/" + domainName
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        print("")
    site_url = url
    r = requests.get(site_url, verify=False)
    filename = site_url.split('/')[-1]
    completeFP = os.path.join(path, filename)
    open(completeFP,'wb').write(r.content)


if __name__ == "__main__":

    url = sys.argv[1]

    (dataResp) = getWebsiteAssets(url)

    now = datetime.now()
    dt_yr = now.strftime("%y")
    dt_mt = now.strftime("%m")
    dt_da = now.strftime("%d")

    path = "./" + dt_yr + "/" + dt_mt + "/" + dt_da

    for key in dataResp.keys():
        if key == "domainName":
            print ("Domain: " + dataResp[key])
            domainName = dataResp[key]
        else:
            print('URL: ' + key)
            print('External Asset List ->')
            if Enquiry(dataResp[key]['externalAsset']):
                print("List is Empty")
            else:
                for allKey in dataResp[key]['externalAsset']:
                    print(allKey)

            print('Internal Asset Raw Data List ->')
            if Enquiry(dataResp[key]['internalAssetRaw']):
                print("List is Empty")
            else:
                for allKey in dataResp[key]['internalAssetRaw']:
                    print(allKey)

            print('Links ->')
            if Enquiry(dataResp[key]['Links']):
                print("List is Empty")
            else:
                for allKey in dataResp[key]['Links']:
                    print(allKey)

            print('Internal Asset AbsolutePath List ->')
            if Enquiry(dataResp[key]['internalAssetComplete']):
                print("List is Empty")
            else:
                for allKey in dataResp[key]['internalAssetComplete']:
                    site_url = allKey
                    print('Download Starting...')
                    print(allKey)
                    webassetsDownload(site_url, path, domainName)
                    print('Download Completed!!!')

        print("\n")
