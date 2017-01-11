import csv

from jinja2 import Markup

BOILERPLATE = "pages.csv"

_TEXTKEY = {}
_TEXTCACHE = {}

with open(BOILERPLATE, "r") as csvf:
  csvr = csv.reader(csvf)
  for row in csvr:
    u_row = [unicode(x, encoding="utf-8") for x in row]
    _TEXTKEY[u_row[0]] = [u_row[1], u_row[2]]

def render_text(inctext):
  title, text = inctext
  #wrap text in text blocks
  dtext = u"""     <div id="tabbed-box_1" class="tabbed-box p-l-1col clearfix">
"""
  for line in text.split("\n"):
    if line:
      dtext += u"""     <div class="text-block">
       <p>"""
      # TODO mark up hrefs?
      dtext += line
      dtext += u"""</p>
     </div>
"""
  dtext += u"     </div>"
  
  return [title, Markup(dtext), text]

def get_boilerplate(textid):
  if textid in _TEXTKEY and textid not in _TEXTCACHE and _TEXTKEY[textid][0]:
    _TEXTCACHE[textid] = render_text(_TEXTKEY[textid])

  if textid in _TEXTCACHE:
    return _TEXTCACHE[textid]

  return [textid, "No description found.", "No description found."]
