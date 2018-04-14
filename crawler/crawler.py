import requests, sys, re, json
from bs4 import BeautifulSoup

def get_all_product_url(region, kind, index):
	url = "https://{}.craigslist.org/search/{}?s={}&hasPic=1".format(region, kind, index)
	session = requests.Session()
	soup = BeautifulSoup(session.get(url, headers = headers).text, "html.parser")
	soup.select(".rows li a")
	prods = soup.select(".rows li p a[href^='http']")
	urls = []
	for prod in prods:
		if prod['href'].find(region) != -1:
			urls.append(prod['href'])
	return urls

def get_max_result(region, kind):
	url = "https://{}.craigslist.org/search/{}?hasPic=1".format(region, kind)
	session = requests.Session()
	soup = BeautifulSoup(session.get(url, headers = headers).text, "html.parser")
	return int(soup.select("span[class='totalcount']")[0].contents[0])

def get_product_info(url):
	session = requests.Session()
	soup = BeautifulSoup(session.get(url, headers = headers).text, "html.parser")
	
	# Get Basic Information about Product
	product = {
		"title": soup.select("#titletextonly")[0].contents[0],
		"price": None,
		"description": soup.select("meta[name=description]")[0]['content'],
		"date": soup.select("time[class='date timeago']")[0]['datetime'],
		"condition": None,
		"imgs": [],
		"url": url
	}
	try:
		product["condition"] = soup.select("p[class='attrgroup'] span b")[0].contents[0]
	except:
		pass
	try:
		product["price"] = int(soup.select(".price")[0].contents[0][1:])
	except:
		product["price"] = -1

	# Get All Links to Images
	scripts = soup.find_all('script')
	pattern = re.compile("var imgList = (.*);")

	for script in scripts:
		if pattern.search(str(script.string)):
			data = pattern.search(str(script.string))
			stock = json.loads(data.groups()[0])
			product["imgs"] = stock
			break

	return product

regions = ["sfbay", "bakersfield", "chico", "fresno", "goldcountry", "hanford", "mendocino",
			"merced", "modesto", "monterey", "redding", "reno", "sacramento", "slo", "santamaria",
			"stockton", "susanville", "visalia", "yubasutter"]

kinds = ["ata", "ppa", "ara", "sna", "pta", "wta", "ava", "baa", "bar", "haa", "bip", "bia", "bpa", "boo",
		"bka", "bfa", "cta", "ema", "moa", "cla", "cba", "syp", "sya", "ela", "gra", "zip", "fua", "gms",
		"foa", "hva", "hsa", "jwa", "maa", "mpa", "mca", "msa", "pha", "rva", "sga", "tia", "tla", "taa",
		"tra", "vga", "waa"]

kinds_name = ["antiques", "appliances", "arts+crafts", "atvs/utvs/snow", "auto parts", "auto wheels & tires", "aviation",
			"baby+kids", "barter", "beauty+hlth", "bike parts", "bikes", "boat parts", "boats", "books", "business", 
			"cars+trucks", "cds/dvd/vhs", "cell phones", "clothes+acc", "collectibles", "computer parts", "computers",
			"electronics", "farm+garden", "free stuff", "furniture", "garage sales", "general", "heavy equipment", "household",
			"jewelry", "materials", "motorcycle parts", "motorcycles", "music instr", "photo+video", "RVs", "sporting", "tickets",
			"tools", "toys+games", "trailers", "video gaming", "wanted"]

headers = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36"}

n_product_page = 120

products = dict((region, []) for region in regions)

for region in regions:
	for kind in kinds:
		max_result = get_max_result(region, kind)
		for i in range(max_result // n_product_page):
			prod_urls = get_all_product_url(region, kind, i * n_product_page)
			for j in range(n_product_page):
				products[region].append(get_product_info(prod_urls[j]))
			sys.stdout.write("{}/{} Products Collected for Region {}, Kind {}\r".format((i + 1) * n_product_page, max_result, region, kinds_name[kinds.index(kind)]))
			sys.stdout.flush()
			
		print (region, kind)







# print (sys.getdefaultencoding())
'''
f = open("c.txt", "wb")

f.write(soup.prettify().encode("utf-8"))

f.close()

'''