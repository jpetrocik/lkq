import lxml.html
from lxml.cssselect import CSSSelector

import re

import requests

import smtplib

import sys

def findText(xpath, tree):
    results = xpath(tree);
    return results[0].text;

url = "http://www.lkqpickyourpart.com/DesktopModules/pyp_vehicleInventory/getVehicleInventory.aspx?store={store}&page=0&filter={query}&sp=&cl=&carbuyYardCode={yard}&pageSize=15&language=en-US";

#car id identifier regex
p = re.compile('[0-9]{4}-[0-9]{4,6}-[0-9]{6}');

#selectors
rowsel = CSSSelector('tr.pypvi_resultRow');
imgsel = CSSSelector('img');
makesel = CSSSelector('td.pypvi_make');
modelsel = CSSSelector('td.pypvi_model');
yearsel = CSSSelector('td.pypvi_year');
datesel = CSSSelector('td.pypvi_date');

old_cars = open('/var/cache/lkq/car.cache').read();

search_terms = sys.argv[5:]; #'volvo%20s60']

fout = open("/var/cache/lkq/car.cache", "a");

message = """From: LKQ PickAPart <no-reply@petrocik.net>
To: {email}
MIME-Version: 1.0
Content-type: text/html
Subject: LKQ Pick Your Part - {store}

<h1>LKQ Pick Your Part - {store}</h1>
<table>
""".format(store=sys.argv[2], email=sys.argv[4])

found = 0;
#search url
for q in search_terms:
	full_url = url.format(query=q,store=sys.argv[1],yard=sys.argv[3]);
	print full_url;
	r = requests.get(full_url);
	tree = lxml.html.fromstring(r.text)
	results = rowsel(tree);

	#loop results
	for row in results:
		car_details = imgsel(row);

		make = findText(makesel, row);
		model = findText(modelsel, row);
		year = findText(yearsel, row);
		date = findText(datesel, row);
		if car_details[0].get('src'):
			carPreview = car_details[0].get('src');
			indexOfQuery = carPreview.index("?");
			carImg = carPreview[:indexOfQuery];

			m = p.search(car_details[0].get('src'));
			car_id = m.group();
			if car_id in old_cars:
				continue
			else:
				fout.write(car_id+'\n');
				message += '<tr><td>' + year + ' ' + make + ' ' + model + '   (Available on: ' + date + ')</td></tr><tr><td><img src="' + carImg  + '"/></td></tr><tr><td>&nbsp;</td></tr>';
				found = 1;


fout.close();

message += "</table>"

if found:
	print message
	smtpObj = smtplib.SMTP( 'hermes.petrocik.net');
	smtpObj.sendmail("john@petrocik.net", "john@petrocik.net", message);  
else:
	print "No cars found";



