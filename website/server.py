import web, json, requests, math, timeit
import numpy as np
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from torch.autograd import Variable
from PIL import Image
import os
import json
import operator
import matplotlib.pyplot as plt
		
urls = (
	'/', 'hello',
	'/upload', 'image',
)
app = web.application(urls, globals())

freq = {"count": 0}
recordCount = 0
ip = "localhost"

class image:
	def GET(self):
		return "Hello World"
	def POST(self):
		data = web.input(file="{}")
		web.debug(data['file'])
		f = open("test.jpg", "wb")
		f.write(data['file'])
		f.close()
		pass

class hello:		
	def __init__(self):
		self.record_count = 0
	
	def GET(self):
		
		search_text = web.input(search_text = "").search_text
		render = web.template.render("templates")
		content = []		
		price_stat = {}
		table_content = {}
		spell_check = []
		sort_rule = int(web.input(sorting = "0").sorting)
		start_time = timeit.default_timer()
		selected_facets = json.loads(web.input(selected_facets = "{}").selected_facets)

		#selected_facets = {
		#	"condition": "new"
		#}
		
		facets = {}
		if search_text != "":
		
			# Spell Check
			url = "http://{}:9200/products/_search".format(ip)
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
			
			url = "http://{}:9200/products/product/_search".format(ip)
			query = {
				"query": {
					"bool": {
						"must": {
							#"fuzzy": {
							#	"title": {
							#		"value": search_text,
							#		"fuzziness": 0
							#	}
							#}
							"multi_match": {
								"fields": ["title^3", "description"],
								"query": search_text
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

			# Filter according to Selected Facets
			
			filtered_prod = []
			for i in range(len(metadata["hits"]["hits"])):
				qualified = True
				for facet_key in selected_facets:
					if (facet_key in metadata["hits"]["hits"][i]["_source"]["facets"]) and (metadata["hits"]["hits"][i]["_source"]["facets"][facet_key].lower() == selected_facets[facet_key].lower()):
						continue
					else:
						qualified = False
						break
				if qualified:
					filtered_prod.append(metadata["hits"]["hits"][i])
			metadata["hits"]["hits"] = filtered_prod


			# Number of Returned Document
	
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

					
					
				# print (sorted(facets.iteritems(), key = lambda (k, v): v["count"], reverse = True))
				facets = sorted(facets.iteritems(), key = lambda (k, v): v["count"], reverse = True)
				
		
		
		global freq
		if len(freq) > 0:
			recom_content = []
			for key in freq:
				if key != "count":
					size = int(float(freq[key]["count"]) / float(freq["count"]) * 21)
					
					max_count = -1
					max_term = ""
					
					for value in freq[key]["values"]:
						if freq[key]["values"][value] > max_count:
							max_count = freq[key]["values"][value]
							max_term = value
							
					query = {
						"query": {
							"bool": {
								"must": {
									"multi_match": {
										"fields": ["title^3", "description"],
										"query": max_term
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
						"size": size
					}
					
					headers = {
						"Content-Type": "application/json"
					}
					
					r = requests.request("POST", "http://{}:9200/products/_search".format(ip), headers = headers, data = json.dumps(query))
					recom_meta = json.loads(r.text)
					
					for i in range(min(size, len(recom_meta["hits"]["hits"]))):
						cur_prod = {}
						cur_prod["description"] = recom_meta["hits"]["hits"][i]["_source"]["description"]
						cur_prod["title"] = recom_meta["hits"]["hits"][i]["_source"]["title"]
						cur_prod["price"] = recom_meta["hits"]["hits"][i]["_source"]["price"]
						cur_prod["url"] = recom_meta["hits"]["hits"][i]["_source"]["url"]
						cur_prod["img_url"] = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/300px-No_image_available.svg.png"
						cur_prod["pid"] = recom_meta["hits"]["hits"][i]["_source"]["pid"]
						if len(recom_meta["hits"]["hits"][i]["_source"]["imgs"]) > 0:
							cur_prod["img_url"] = recom_meta["hits"]["hits"][i]["_source"]["imgs"][0]["url"]
						recom_content.append(cur_prod)
					
			print (len(recom_content))
			pass
			
		
		price_stat["time"] = timeit.default_timer() - start_time
		return render.index(search_text, content, price_stat, table_content, spell_check, sort_rule, facets, json.dumps(selected_facets), selected_facets, recom_content)
		
	def POST(self):
		data = web.data()
		global recordCount
		global freq
		#if recordCount % 50 == 0:
		#	freq = {}
		recordCount += 1
		
		print (recordCount)
		print (web.data())
		
		pid_list = data.split(',')
		print (pid_list)
		for i in range(len(pid_list)):
			if pid_list[i] == "":
				continue
			pid = int(pid_list[i])
			url = "http://{}:9200/products/product/{}".format(ip, pid)
			r = requests.request("GET", url)
			rjson = json.loads(r.text)
			
			for key in rjson['_source']['title'].split(' '):
				if not (rjson['_source']['kind'] in freq):
					freq[rjson['_source']['kind']] = {
						"count": 0,
						"values": {}
					}
				freq[rjson['_source']['kind']]["values"].update({key.lower() : freq[rjson['_source']['kind']]["values"].get(key.lower(), 0) + 1})
			freq[rjson['_source']['kind']]["count"] += 1
			freq["count"] += 1
		print (freq)
	
		pass
		
		
if __name__ == "__main__":
	app.run()
