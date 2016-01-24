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
p = re.compile('[0-9]{4}-[0-9]{4}-[0-9]{6}');

#selectors
rowsel = CSSSelector('tr.pypvi_resultRow');
imgsel = CSSSelector('img');
makesel = CSSSelector('td.pypvi_make');
modelsel = CSSSelector('td.pypvi_model');
yearsel = CSSSelector('td.pypvi_year');
datesel = CSSSelector('td.pypvi_date');

old_cars = open('/var/cache/lkq/car.cache').read();

search_terms = ['volvo%20s80', 'volvo%20xc70', 'volvo%20v70', 'volvo%20s60']

fout = open("/var/cache/lkq/car.cache", "a");

message = """From: LKQ PickAPart <john@petrocik.net>
To: John Petrocik <john@petrocik.net>
MIME-Version: 1.0
Content-type: text/html
Subject: LKQ Pick Your Part

<h1>LKQ Pick Your Part - {store}</h1>
<table>
<tr style="color:#4a4a4a;font-size:20px;font-weight:bold;vertical-align:top;"><td></td><td>Make</td><td>Model</td><td>Year</td><td>Date</td></tr>
""".format(store=sys.argv[2])

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
			m = p.search(car_details[0].get('src'));
			car_id = m.group();
			if car_id in old_cars:
				continue
			else:
				fout.write(car_id+'\n');
				message += '<tr style="color:#4a4a4a;font-size:20px;font-weight:bold;vertical-align:top;"><td><img src="' + car_details[0].get('src') + '"/></td><td>' + make + '</td><td>' + model + '</td><td>' + year + '</td><td>' + date + '</td></tr>';
				found = 1;


fout.close();

message += "</table>"

if found:
	print message
	smtpObj = smtplib.SMTP( 'hermes.petrocik.net');
	smtpObj.sendmail("john@petrocik.net", "john@petrocik.net", message);  
else:
	print "No cars found";



