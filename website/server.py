import web, json, requests, math, timeit
		
urls = (
	'/(.*)', 'hello'
)
app = web.application(urls, globals())

class hello:		
	def GET(self, data):
		search_text = web.input(search_text = "").search_text
		render = web.template.render("templates")
		content = []		
		price_stat = {}
		table_content = {}
		spell_check = []
		sort_rule = int(web.input(sorting = "0").sorting)
		start_time = timeit.default_timer()
		facets = {}
		if search_text != "":
		
			# Spell Check
			url = "http://localhost:9200/products/_search"
			query = {
				"suggest": {
					"my-suggest": {
						"text": search_text,
						"term":	{
							"field": "title"
						}
					}
				}
			}
			headers = {
				"Content-Type": "application/json"
			}
			r = requests.request("POST", url, headers = headers, data = json.dumps(query))
			metadata = json.loads(r.text)
			
			for i in range(len(metadata["suggest"]["my-suggest"][0]["options"])):
				spell_check.append(metadata["suggest"]["my-suggest"][0]["options"][i]["text"])
			
			url = "http://localhost:9200/products/product/_search"
			query = {
				"query": {
					"bool": {
						"must": {
							"fuzzy": {
								"title": {
									"value": search_text,
									"fuzziness": 0
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
			
			print (sort_rule)
			if sort_rule == 1:
				query["sort"] = [
					{
						"price": {"order": "asc"}
					}
				]
			elif sort_rule == 2:
				query["sort"] = [
					{
						"price": {"order": "desc"}
					}
				]
			elif sort_rule == 3:
				query["sort"] = [
					{
						"date": {"order": "desc"}
					}
				]
			elif sort_rule == 4:
				query["sort"] = [
					{
						"date": {"order": "asc"}
					}
				]
			
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
			metadata = json.loads(r.text)
			n_result = min(len(metadata["hits"]["hits"]), 21)
			

			
			if n_result > 0:
				# Create List for Products
				content = []
				for i in range(n_result):
					cur_prod = {}
					cur_prod["description"] = metadata["hits"]["hits"][i]["_source"]["description"]
					cur_prod["title"] = metadata["hits"]["hits"][i]["_source"]["title"]
					cur_prod["price"] = metadata["hits"]["hits"][i]["_source"]["price"]
					cur_prod["url"] = metadata["hits"]["hits"][i]["_source"]["url"]
					cur_prod["img_url"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/300px-No_image_available.svg.png"
					cur_prod["pid"] = metadata["hits"]["hits"][i]["_source"]["pid"]
					if len(metadata["hits"]["hits"][i]["_source"]["imgs"]) > 0:
						cur_prod["img_url"] = metadata["hits"]["hits"][i]["_source"]["imgs"][0]["url"]
					content.append(cur_prod)
				
			
				# Price Statistics
				table_content = {
					'labels' : '',
					'data': ''
				}
			
				max_price = 0.
				min_price = 1e10
				valid_count = 0.
				price_sum = 0.
				n_interval = 8.
			
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
				
				
				# Facets
				

				for i in range(len(metadata["hits"]["hits"])):
					for facet_key in metadata["hits"]["hits"][i]["_source"]["facets"]:
						facet_value = metadata["hits"]["hits"][i]["_source"]["facets"][facet_key].lower()
						if facet_key in facets:
							if facet_value in facets[facet_key]["value"]:
								facets[facet_key]["value"][facet_value] += 1
							else:
								facets[facet_key]["value"][facet_value] = 1
							facets[facet_key]["count"] += 1
						else:
							facets[facet_key] = {
								"value": {
									facet_value: 1
								},
								"count": 1
							}
							
							
				for facet_key in facets:
					facets[facet_key]["value"] = sorted(facets[facet_key]["value"].iteritems(), key = lambda (k, v): v, reverse = True)

					
					
				print (sorted(facets.iteritems(), key = lambda (k, v): v["count"], reverse = True))
				facets = sorted(facets.iteritems(), key = lambda (k, v): v["count"], reverse = True)
				
			
		
		price_stat["time"] = timeit.default_timer() - start_time
		return render.index(search_text, content, price_stat, table_content, spell_check, sort_rule, facets)

if __name__ == "__main__":
	app.run()
