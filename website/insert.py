import requests, sys, re, json, os

files = os.listdir("data")

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

index_count = 0

for i in range(len(files)):
	f = open("data/" + files[i], "r")
	metadata = json.loads(f.readline())
	for j in range(len(metadata)):
		url = "http://localhost:9200/products/product/" + str(index_count)
		headers = {
			"Content-Type": "application/json"
		}
		metadata[j]["kind"] = kinds[i]
		r = requests.request("PUT", url, headers = headers, data = json.dumps(metadata[j]))
		if j == 0:
			print (r.text)
		if (index_count + 1) % 500 == 0:
			print ("Finished {} Insertion".format(index_count + 1))
		index_count += 1
