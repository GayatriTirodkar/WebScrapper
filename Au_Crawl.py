import requests
from bs4 import BeautifulSoup
import json
import time
import datetime
import os

def execute(keyword):
	#The post request to get the search records
	print "Executing Crawler....."
        url = "https://www.woolworths.com.au/apis/ui/Search/products"
        post_dict = {}
	post_dict['Filters'] = {}
	post_dict['Location'] = "/shop/search/products?searchTerm={}".format("%20".join(keyword.split()))
	post_dict['PageNumber'] = '1'
        post_dict['PageSize'] = '24'
	post_dict['SearchTerm'] = keyword
	post_dict['SortType'] = 'TraderRelevance'
        search_result_page = requests.post(url, post_dict)
	result_json = json.loads(search_result_page.text)
	print "Calling Parser for Page: 1"
	generate_json(result_json,"1")
	

	#iterating to get data from page 2 onwards
	print "Check for multiple pages if any..."
	product_count = int(result_json['SearchResultsCount'])
	if product_count > 24:
		end_page_index = (product_count / 24) + 1
		print "Total number of pages: {} found. Starting to parse page: 2 onwards.".format(str(len(range(1, end_page_index + 1))))
		for i in range(2, end_page_index + 1):
			print "Crawling page: {}".format(str(i))
			post_dict['IsSpecial'] = 'false'
			post_dict['Location'] = "https://www.woolworths.com.au/apis/ui/Search/products/shop/search/products?searchTerm={}&pageNumber={}".format("%20".join(keyword.split()), str(i))
			post_dict['PageNumber'] = i
			search_result_page = requests.post(url, post_dict)
			result_json = json.loads(search_result_page.text)
			print "Calling parser for page: {}".format(str(i))
			generate_json(result_json, str(i))
	

def generate_json(result_json, pgno):
	print "Executing parser for page: {}".format(pgno)
	time_stamp = time.time()
	output_json = []
	for ele in result_json['Products']:
        	product_arr = []
		product_dict = {}
                product_dict['main_product_name'] = ele['Name'].encode('ascii') #main product name
                for index, sub_ele in enumerate(ele['Products']):
			previous_price = ele['Products'][index]['CentreTag']['TagContent'].encode('ascii') if ele['Products'][index]['CentreTag']['TagContent'] is not None else ""
			soup = BeautifulSoup(previous_price, 'html.parser')
  			previous_price = soup.text
                	sub_product_dict = {}
                        sub_product_dict['name'] = ele['Products'][index]['Name'].encode('ascii')
                        sub_product_dict['price'] = ele['Products'][index]['Price']
			sub_product_dict['cup_string'] = ele['Products'][index]['CupString']
			sub_product_dict['previous_price'] =  previous_price
                        sub_product_dict['currency'] = 'AUD'
                        sub_product_dict['package_size'] = ele['Products'][index]['PackageSize'].encode('ascii')
                        sub_product_dict['weight_in_grams'] = ele['Products'][index]['UnitWeightInGrams']
			sub_product_dict['in_stock'] = ele['Products'][index]['IsInStock']
                        sub_product_dict["brand"] = ele['Products'][index]['Brand'].encode('ascii')
                        sub_product_dict["description"] = ele['Products'][index]['FullDescription'].encode('ascii')
                        product_arr.append(sub_product_dict)
                        product_dict['details'] = product_arr
                product_dict['crawler_date_time'] = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')

		output_json.append(product_dict)

	with open('output_files/page_json_{}.json'.format(pgno), 'wb') as file_obj:
		file_obj.write(json.dumps(output_json))
		print "Succesfull creted json for page: {} and saved in {}/page_json_{}.json".format(pgno, os.listdir(os.getcwd())[-1], pgno)

if __name__ == "__main__":
        search_term = "Gillette Razor".lower()
	execute(search_term)
