import requests, re, dominate, pytz
from bs4 import BeautifulSoup
from dominate.tags import *
from os import path
from datetime import datetime
folder = path.dirname(path.realpath(__file__))
allb = {"George": ["148","155","188"], "Lakeside": ["133","139","208"], "Southwest": ["169","157"], "Central": ["196","189","197"]}
def get_buses():
    dtsoitext=requests.get("https://www.sdale.org/o/don-tyson-school-of-innovation/live-feed").text

    soup=BeautifulSoup(dtsoitext,"html.parser")
    posts=soup.find_all("div",class_="status")
    full_busnums = []
    busnums = []
    for post in posts:
        timeAgo = post.find_next("div", class_="date-author").get_text().replace("about", "").strip()
        if ("hour" in timeAgo or "minute" in timeAgo) and ("hour" not in timeAgo or int(timeAgo.split(" ")[0]) <= 15) and ("bus" in (post.get_text()).lower() and "run" in (post.get_text()).lower()):
            bus_post = post.get_text()
            localBusnums = re.findall(r"#* *(([0-9]|/)*)", bus_post.lower())
            busnums += [i[0] for i in localBusnums if len(i[0]) > 0]
    #print("\033[36mThe following busses from DTSOI are not running Today: ",busnums)
            local_full_busnums = bus_post.split("\n")[1:]
            full_busnums += [i.strip() for i in local_full_busnums if "\r" != i]
    return (busnums,full_busnums)

def web_gen():
    busnums= get_buses()
    seen_buses = []
    full_buses = busnums[1]
    numobus=0
    doc = dominate.document(title="DTSOI Bus Status")
    with doc.head:
        link(rel='stylesheet',href='index.css')
        link(href='https://fonts.googleapis.com/css?family=Comfortaa', rel='stylesheet')
        meta(name="viewport", content="width=device-width, intitial-scale=1")
        link(rel="apple-touch-icon", sizes="180x180", href="/apple-touch-icon.png")
        link(rel="icon", type="image/png", sizes="32x32", href="/favicon-32x32.png")
        link(rel="icon", type="image/png", sizes="16x16", href="/favicon-16x16.png")
        link(rel="manifest", href="/site.webmanifest")       
    with doc:
        with div():
            img(src="SOIBus.png", _class="timage")
        with div():
            h1("DTSOI Bus Status", _class = "title")
            hr(_class = "line")
            p("Last Updated: ",(datetime.now(pytz.timezone("America/Chicago")).strftime("%a %b %d %I:%M %p, %Y ")),_class = "subtitle")
            for i in full_buses:
                numobus+=1
            if numobus == 0:
                p("|")
                p(mark("All buses are running at this time"), _class="subtitle hiyell")
            for school in allb.keys():
                p("|")
                p(school,_class = "subtitle")
                for bus in allb[school]:
                    if bus in busnums[0]:
                        p(mark(f"Bus #{bus} is not running"), _class = "hiyell")
                        seen_buses.append(bus)
                    else:
                        p(f"Bus #{bus} is running")
        with div():
            doextrabus = False
            for extrabus in full_buses:
                if extrabus not in seen_buses:
                    doextrabus = True
            if doextrabus == True:             
                hr(_class = "line")
                p(mark("These buses are also not running:"), _class = "subtitle hiyell")
            for i in full_buses:
                seen = False
                for seenbus in seen_buses:
                    if seenbus in i:
                        seen = True
                if seen == False:
                    p(i)
    with open(path.join(folder,"public/index.html"),"w") as File:
        File.write(doc.render())
web_gen()