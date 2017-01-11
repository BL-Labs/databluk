import os, sys, shutil
from jinja2 import Environment, PackageLoader
import csv

from boilerplate import get_boilerplate

env = Environment(loader=PackageLoader("dbu", "templates"))
item_t = env.get_template("item.html")
col_t = env.get_template("col.html")
base_t = env.get_template("rootpage.html")

DEPLOY_BASE = "/cygdrive/z"

def get_dl_path(collection, filename):
  if filename.startswith("http"):
    return ""
  return os.path.join(DEPLOY_BASE, collection, filename)

# from http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size#1094933
def sizeof_fmt(num, suffix='B'):
  for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
    if abs(num) < 1024.0:
      return "%3.1f%s%s" % (num, unit, suffix)
    num /= 1024.0
  return "%.1f%s%s" % (num, 'Yi', suffix)

def filesize(filepath):
  if filepath:
    if os.path.exists(filepath):
      st = os.stat(filepath)
      return sizeof_fmt(st.st_size)
    else:
      return "NO FILE FOUND"
  return ""

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

def base_page(collections):
  datapkg = {'cols': collections}
  datapkg['boilerplate_text'] = {x:get_boilerplate(x)[0] for x in collections}
  datapkg['title'] = u"data.bl.uk"
  datapkg['path'] = ""
  datapkg['dcdescription'] = "A collection of datasets released by the British Library"
  datapkg['mainpage'] = get_boilerplate("mainpage")
  datapkg['rootoffset'] = ""
  return base_t.render(**datapkg)
  

def collection_page(datapkg):
  col_name = datapkg['name']
  datapkg['readabletitle'], datapkg['htmldescription'], datapkg['dcdescription'] = get_boilerplate(datapkg['name'])
  datapkg['title'] = datapkg['readabletitle'] or u"Dataset Collection" 
  datapkg['collection'] = datapkg['name']
  datapkg['path'] = ["/" + datapkg['name']]
  datapkg['rootoffset'] = ""
  return col_t.render(**datapkg)


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
  datapkg['rootoffset'] = ""
  datapkg['itemimg'] = ""
  if line['img']:
    datapkg['itemimg'] = line['img']
    datapkg['itemimgcaption'] = line['imgcaption'] or datapkg['title']
  datapkg['department'] = line['department']
  datapkg['publisher'] = line['dataset publisher']
  datapkg['collection'] = line['dataset collection']
  datapkg['licencelink'] = line['usage terms']
  datapkg['usage'] = line['how to use data']
  datapkg['curator'] = line['curator']
  datapkg['project'] = line['project name']
  datapkg['contentdates'] = line['Date range of content']
  # FIXME URL needs proper encoding of the collection name
  datapkg['canonicalurl'] = "http://data.bl.uk/" + line['dataset collection'] + "/" + line['dataset short name'] + ".html"
  datapkg['dataset_collection'] = get_boilerplate(line['dataset collection'])
  datapkg['filename'] = [line['filename']]
  datapkg['filesize'] = [filesize(get_dl_path(line['dataset collection'], line['filename']))]
  

  datapkg['data'] = {'title': line['dataset title (for humans)']}
  datapkg['data']['dcdescription'] =  line['description']
  datapkg['data']['creator'] =  line['creator']
  datapkg['data']['publisher'] =  line['dataset publisher']
  datapkg['data']['date'] =  line['created']
  datapkg['data']['format'] = [line['format']]
  datapkg['data']['licence'] = [line['licence']]
  datapkg['data']['doi'] =  line['doi']
  datapkg['data']['contentdates'] = line['Date range of content']
  datapkg['data']['licencelink'] = [line['usage terms']]

  # Handle multiple representations
  if "," in line['filename']:
    print(line['filename'])
    datapkg['filename'] = line['filename'].split(",")
    datapkg['filesize'] = [filesize(get_dl_path(line['dataset collection'] ,f)) for f in line['filename'].split(",")]
    datapkg['data']['format'] = line['format'].split(",")
    datapkg['data']['licence'] = line['licence'].split(",")
    datapkg['data']['licencelink'] = line['usage terms'].split(",")

  # create a convenience structure
  datapkg['zfiles'] = zip(datapkg['filename'], datapkg['filesize'], datapkg['data']['format'], datapkg['data']['licence'], datapkg['data']['licencelink'])

  return datapkg

if __name__ == "__main__":
  if os.path.exists("datasets.csv"):
    clean()
    deploy_boilerplate()
    # get boilerplate text values
    
    with open("datasets.csv", "r") as csvf:
      csvdoc = csv.DictReader(csvf)
      collections = {}
      for row in csvdoc:
        line = {unicode(key, "utf-8"): unicode(value, "utf-8") for key, value in row.iteritems()}
        if line['dataset short name'] != "" and line['isreleased'] == "y":
          try:
            os.remove(htmlfilename(line))
          except OSError:
            pass
           
          
          datapkg = datamapping(line)
          if not os.path.exists(os.path.join("www", line['dataset collection'])):
            os.mkdir(os.path.join("www", line['dataset collection']))
            collections[line['dataset collection']] = []
          with open(os.path.join("www", htmlfilename(line)), "w") as outp:
            collections[line['dataset collection']].append({key: datapkg[key] for key in ['title', 'dcdescription', 'canonicalurl', 'data']})
            collections[line['dataset collection']][-1]['collection'] = line['dataset collection']
            outp.write(basic_item(datapkg).encode("utf-8"))
      
      for key in sorted(collections.keys()):
        # crete the collection pages for the datasets
        with open(os.path.join("www", key, "index.html"), "w") as outp:
          datapkg = {'data': collections[key], 'name': key}
          outp.write(collection_page(datapkg).encode("utf-8"))
      with open(os.path.join("www", "index.html"), "w") as outp:
        outp.write(base_page(collections).encode("utf-8"))
            
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
