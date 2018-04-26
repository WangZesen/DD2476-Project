import web, json, requests
		
urls = (
	'/(.*)', 'hello'
)
app = web.application(urls, globals())

class hello:		
	def GET(self, data):
		search_text = web.input(search_text = "").search_text
		print ("search_text = " + search_text)
		render = web.template.render("templates")
		content = ""		
		price_stat = {}
		if search_text != "":
			url = "http://localhost:9200/products/product/_search"
			query = {
				"query": {
					"match": {
						"title": search_text
					}
				},
				"size": 10000
			}
			headers = {
				"Content-Type": "application/json"
			}

			r = requests.request("POST", url, headers = headers, data = json.dumps(query))
			
			metadata = json.loads(r.text)
			
			result_n = min(len(metadata["hits"]["hits"]), 20)
			
			content = ""
			
			for i in range(result_n):
				content = content + "<li> Title = " + metadata["hits"]["hits"][i]["_source"]["title"] + ", Price = " + str(metadata["hits"]["hits"][i]["_source"]["price"]) + '    <a href="{}">'.format(metadata["hits"]["hits"][i]["_source"]["url"]) + "Product Link</a><br>"
				if len(metadata["hits"]["hits"][i]["_source"]["imgs"]) > 0:
					content += '<img src="{}">'.format(metadata["hits"]["hits"][i]["_source"]["imgs"][0]["url"])
				content += "</li>"
			
			content = '<ol>' + content + '</ol>'
			
			
			max_price = 0
			min_price = 1e10
			valid_count = 0.
			price_sum = 0.
			
			for i in range(len(metadata["hits"]["hits"])):
				if metadata["hits"]["hits"][i]["_source"]["price"] != -1:
					max_price = max(max_price, metadata["hits"]["hits"][i]["_source"]["price"])
					min_price = min(min_price, metadata["hits"]["hits"][i]["_source"]["price"])
					valid_count += 1
					price_sum += metadata["hits"]["hits"][i]["_source"]["price"]
			print (max_price)
			print (min_price)
			print (price_sum / valid_count)
			price_stat["max"] = max_price
			price_stat["min"] = min_price
			price_stat["average"] = price_sum / valid_count
			
		
		table_content = {
			'labels' : '["Red", "Blue", "Yellow", "Green", "Purple", "Orange"]',
			'data': '[12, 19, 3, 5, 2, 3]'
		}	
		return render.index(search_text, content, price_stat, table_content)

if __name__ == "__main__":
	app.run()
