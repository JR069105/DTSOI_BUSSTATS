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
    bus_post = [i.get_text() for i in posts if "buses" in i.get_text() and "run" in i.get_text()][0]
    busnums = re.findall(r"bus # (([0-9]|/)*)", bus_post.lower())
    busnums = [i[0] for i in busnums]
    #print("\033[36mThe following busses from DTSOI are not running Today: ",busnums)
    full_busnums = bus_post.split("\n")[1:]
    full_busnums = [i.strip() for i in full_busnums if "\r" != i]
    return (busnums,full_busnums)

def web_gen():
    busnums= get_buses()
    seen_buses = []
    full_buses = busnums[1]
    doc = dominate.document(title="DTSOI bus post status")
    with doc.head:
        link(rel='stylesheet',href='index.css')
        link(href='https://fonts.googleapis.com/css?family=Comfortaa', rel='stylesheet')
        meta(name="viewport", content="width=device-width, intitial-scale=1")
    with doc:
        with div():
            h1("DTSOI Buses Status", _class = "title")
            hr(_class = "line")
            p("Last Updated: ",(datetime.now(pytz.timezone("America/Chicago")).strftime("%a %b %m %I:%M %p, %Y ")),_class = "subtitle")
            for school in allb.keys():
                p("|")
                p(school,_class = "school")
                for bus in allb[school]:
                    if bus in busnums[0]:
                        p(f"Bus #{bus} is not running")
                        seen_buses.append(bus)
                    else:
                        p(f"Bus #{bus} is running")
        with div():
            hr(_class = "line")
            p("These buses are also not running:",_class = "subtitle")
            for i in full_buses:
               if re.search(r"bus # (([0-9]|/)*)", i.lower())[0].split(" ")[2] not in seen_buses:
                p(i)
    with open(path.join(folder,"public/index.html"),"w") as File:
        File.write(doc.render())
web_gen()
