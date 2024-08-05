# bash register DOIs example:
for i in {1..7}
do curl -H"Content-Type: application/xml;charset=UTF-8" -XPOST -T ../doi_md/pel0$i.xml https://[user]:[password]@mds.datacite.org/metadata
curl -XPOST --basic --data doi=10.21250/pel0$i --data url="https://data.bl.uk/pelagios/pel0$i.html" https://[user]:[password]@mds.datacite.org/doi

