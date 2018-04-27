import web, json, requests, math
		
urls = (
	'/(.*)', 'hello'
)
app = web.application(urls, globals())

class hello:		
	def GET(self, data):
		search_text = web.input(search_text = "").search_text
		render = web.template.render("templates")
		content = ""		
		price_stat = {}
		table_content = {}
		if search_text != "":
			url = "http://localhost:9200/products/product/_search"
			query = {
				"query": {
					"bool": {
						"must": {
							"fuzzy": {
								"title": {
									"value": search_text,
									"fuzziness": "AUTO"
								}
							}
						},
						"filter": {
							"range": {
								"price": {
									"gt": 0
								}
							}
						}
					}
					
				},
				"size": 10000
			}
			
			if web.input(price = "").price != "":
				lowest = float(web.input(price = "").price.split(",")[0])
				highest = float(web.input(price = "").price.split(",")[1])
				query["query"]["bool"]["filter"]["range"]["price"] = {
					"gte": int(lowest),
					"lte": int(highest)
				}
			
			headers = {
				"Content-Type": "application/json"
			}

			r = requests.request("POST", url, headers = headers, data = json.dumps(query))
			print (r.text)
			metadata = json.loads(r.text)
			n_result = min(len(metadata["hits"]["hits"]), 20)
			

			
			if n_result > 0:
				# Create List for Products
				content = ""
				for i in range(n_result):
					content += "<li> Title = " + metadata["hits"]["hits"][i]["_source"]["title"] 
					content += ", Price = " + str(metadata["hits"]["hits"][i]["_source"]["price"]) 
					content += '    <a href="{}">'.format(metadata["hits"]["hits"][i]["_source"]["url"]) 
					content += "Product Link</a><br>"
					if len(metadata["hits"]["hits"][i]["_source"]["imgs"]) > 0:
						content += '<img src="{}">'.format(metadata["hits"]["hits"][i]["_source"]["imgs"][0]["url"])
					content += "</li>"
				content = '<ol>' + content + '</ol>'
			
				# Price Statistics
				table_content = {
					'labels' : '',
					'data': ''
				}
			
				max_price = 0.
				min_price = 1e10
				valid_count = 0.
				price_sum = 0.
				n_interval = 10.
			
				for i in range(len(metadata["hits"]["hits"])):
					if metadata["hits"]["hits"][i]["_source"]["price"] != -1:
						max_price = max(max_price, float(metadata["hits"]["hits"][i]["_source"]["price"]))
						min_price = min(min_price, float(metadata["hits"]["hits"][i]["_source"]["price"]))
						valid_count += 1
						price_sum += metadata["hits"]["hits"][i]["_source"]["price"]

				counts = [0 for i in range(int(n_interval))]
				
				if max_price - min_price > 0:
					for i in range(len(metadata["hits"]["hits"])):
						if metadata["hits"]["hits"][i]["_source"]["price"] != -1:
							interval_n = int(math.floor((metadata["hits"]["hits"][i]["_source"]["price"] - min_price) / ((max_price - min_price) / n_interval)))
							if interval_n >= n_interval:
								interval_n -= 1
							counts[interval_n] += 1
			
					for i in range(int(n_interval)):
						table_content['data'] += str(counts[i]) + ","
					table_content['data'] = "[" + table_content['data'][:-1] + "]"
				
					for i in range(int(n_interval)):
						table_content['labels'] += '"' + '%.2f' % (min_price + (max_price - min_price) / n_interval * i) + " to " + '%.2f' % (min_price + (max_price - min_price) / n_interval * (i + 1)) + '",'
					table_content['labels'] = "[" + table_content['labels'][:-1] + "]"
				else:
					table_content['labels'] = "[]"
					table_content['data'] = "[]"
				price_stat["max"] = max_price
				price_stat["min"] = min_price
				price_stat["average"] = price_sum / valid_count
				price_stat["n"] = len(metadata["hits"]["hits"])
			
				
			
		
		
		return render.index(search_text, content, price_stat, table_content)

if __name__ == "__main__":
	app.run()
