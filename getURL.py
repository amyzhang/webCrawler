import urllib
from urlparse import urlparse
from urlparse import urljoin
from collections import Counter
import re

reg=re.compile('[a-z0-9/\-_]+$')

with open('inURLs.txt') as f:
    content = f.readlines()

URLs = map(lambda s: s.strip(), content)

## isEvent is mostly for the workshopsf.org link, if using other links I
## would check wordcounts for various key words more, otherwise I get too
## many false positives trying to make this function more general.    
def isEvent(body):
    c = Counter(w.lower() for w in re.findall('(workshop)', body))
    return sum(c.values())>3

def getnewLinks(page,prevLinks, rootdomain):
    try:
        response = urllib.urlopen(page[:-1])
    except urllib.URLError, e:
        print e.code
        print e.read()
        return []
    html = response.read()

    links,pos,allFound=[],0,False
    while not allFound:
        aTag=html.find("<a href=",pos)
        if aTag>-1:
            href=html.find('"',aTag+1)
            endHref=html.find('"',href+1)
            url=html[href+1:endHref]
            if len(url)>0:
                if url[:7]!="http://" and bool(reg.match(url)):
                    url = urljoin(page, url)
                if url[:7]=="http://":
                    if url[-1]=="/":
                        url=url[:-1]
                    if not url in links and not url in prevLinks and rootdomain in url:
                        links.append(url)
            closeTag=html.find("</a>",aTag)
            pos=closeTag+1
        else:
            allFound=True   
    return links

for seed in URLs:
    print 'looking at ' + seed
    rootdomain = '.'.join(urlparse(seed).netloc.split('.')[-2:])

    if seed[-1]=="/":
        seed = seed[0:-1]
    toCrawl=[seed]
    prior = seed
    while len(prior)>len(seed[0:11+len(rootdomain)]):
        prior = prior[0:prior.rfind('/')]
        toCrawl.append(prior+'/')
    otherevents = []
    crawled=[]
    while toCrawl:
        if len(otherevents) >= 10:
            break
        url=toCrawl.pop(0)
        #print url
        crawled.append(url)
        newLinks=getnewLinks(url,crawled, rootdomain)
        toCrawl=toCrawl + newLinks
        for link in newLinks:
            if link not in otherevents and seed not in link:
                if "event" in link:
                    otherevents.append(link)
                else:
                    try:
                        response = urllib.urlopen(link)
                    except urllib.URLError, e:
                        print e.code
                        print e.read()
                        continue
                    body = response.read()
                    if isEvent(body):
                        otherevents.append(link)
    file = open("outURLs.txt", "a")
    for event in otherevents:
        file.write(event+'\n')
    file.close()
