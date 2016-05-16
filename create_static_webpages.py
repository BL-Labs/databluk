import os, sys, shutil
from jinja2 import Environment, PackageLoader
import csv

env = Environment(loader=PackageLoader("dbu", "templates"))
item_t = env.get_template("item.html")

def clean():
  try:
    shutil.rmtree("www")
  except OSError:
    pass
  os.mkdir("www")

def deploy_boilerplate():
  shutil.copytree("dbu/js", "www/js")
  shutil.copytree("dbu/fonts", "www/fonts")
  shutil.copytree("dbu/css", "www/css")
  shutil.copytree("dbu/images", "www/images")
  shutil.copytree("dbu/backgrounds", "www/backgrounds")

def basic_item(datapkg):
  # "base.html" requires:
  # title
  # dcidentifier
  # dcdescription
  # ogurl
  # keywords
  # dccreated
  # canonicalurl 
  # pagetitle
  # Optional: sidebar
  # Optional: sidebarcontent = {'title': .., 'description': ..., 'url'=...}
  # "item.html"
  # 
  return item_t.render(**datapkg)

def htmlfilename(line):
  col = line['dataset collection']
  if col:
    return col + "/" + line['dataset short name'] + ".html"
  else:
    return "misc/" + line['dataset short name'] + ".html"

def datamapping(line):
  datapkg = {}
  datapkg['title'] = line['dataset title (for humans)']
  datapkg['dcdescription'] = line['description']
  datapkg['contentnotes'] = line['content notes']
  datapkg['keywords'] = line['keywords']
  datapkg['dccreated'] = line['created']
  datapkg['pagetitle'] = datapkg['title']
  datapkg['path'] = [line['dataset collection']]
  datapkg['rootoffset'] = "../"
  datapkg['itemimg'] = line['img'] or "images/generic.jpg"
  datapkg['itemimgcaption'] = line['imgcaption'] or datapkg['title']
  datapkg['department'] = line['department']
  datapkg['publisher'] = line['dataset publisher']
  datapkg['collection'] = line['dataset collection']
  datapkg['usage'] = line['usage terms']
  datapkg['curator'] = line['curator']
  datapkg['project'] = line['project name']
  datapkg['contentdates'] = line['Date range of content']
  datapkg['canonicalurl'] = "http://data.bl.uk/" + line['dataset collection'] + "/" + line['dataset short name']

  datapkg['data'] = {'title': line['dataset title (for humans)']}
  datapkg['data']['dcdescription'] =  line['description']
  datapkg['data']['creator'] =  line['creator']
  datapkg['data']['publisher'] =  line['dataset publisher']
  datapkg['data']['date'] =  line['created']
  datapkg['data']['format'] =  line['format']
  datapkg['data']['licence'] =  line['licence']

  return datapkg

if __name__ == "__main__":
  if os.path.exists("datasets.csv"):
    clean()
    deploy_boilerplate()
    with open("datasets.csv", "r") as csvf:
      csvdoc = csv.DictReader(csvf)
      col = set()
      for row in csvdoc:
        line = {unicode(key, "utf-8"): unicode(value, "utf-8") for key, value in row.iteritems()}
        if line['dataset short name'] != "":
          try:
            os.remove(htmlfilename(line))
          except OSError:
            pass
           
          col.add(line['dataset collection'])
          if not os.path.exists(os.path.join("www", line['dataset collection'])):
            os.mkdir(os.path.join("www", line['dataset collection']))
          with open(os.path.join("www", htmlfilename(line)), "w") as outp:
            datapkg = datamapping(line)
            outp.write(basic_item(datapkg).encode("utf-8"))
            
  else:
    print("No 'datasets.csv' -> producing test page instead.")
    clean()
    deploy_boilerplate()
    datapkg = {"title": "Test page", "dcidentifier": "DC identifier, likely DOI once given",
               "dcdescription": "Basic DC description of the item. Abstract length",
               "ogurl": "No idea", "keywords": "basic, keyword, list",
               "dccreated": "2016-05-16", "canonicalurl": "Real URL for the item",
               "pagetitle": "Title that appears at the top of the page",
               "itemimg": "images/testimage.png", "itemimgcaption": "Test image for the item",
               "data": {'title': "Test item", 'creator':'BL Labs', 'publisher':'BL', 'date':'2016-05-16', 'format':'application/zip', 'licence':"CC3.0-BY"},
               }
    with open("www/test.html", "w") as outp:
      outp.write(basic_item(datapkg).encode("utf-8"))
