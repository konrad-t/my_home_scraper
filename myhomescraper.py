import scrape_functions as sf
import requests
import pandas as pd
import json
from datetime import date
from pandas.io.json import json_normalize



#REQUESTS FOR PROPERTY URLS TO GET KEYS

url = "https://api.myhome.ie/search?ApiKey=5f4bc74f-8d9a-41cb-ab85-a1b7cfc86622"
headers = {'Content-Type':'application/json;charset=UTF-8'}
for_sale_body = {'body':'{{"SearchRequest":{{"IsSaleAgreed":"","IsSold":false,"IsAuction":"","UseFreeTextSearchForKeywords":false,"SearchContent":false,"Query":"","PropertyIds":[],"GroupIds":[],"ChannelIds":[1],"PropertyTypeIds":[],"PropertyClassIds":[1],"PropertyStatusIds":[2,12],"SaleTypeIds":[],"RegionId":"2168","LocalityIds":[],"NegotiatorIds":[],"EnergyRatings":[],"Destinations":[],"MinEnergyRating":"","MaxEnergyRating":"","MinPrice":"","MaxPrice":"","MinBeds":"","MaxBeds":"","MinBathrooms":"","MinSize":"","MaxSize":"","PreSixtyThree":false,"SortBy":"Most Recent","PropertyClassId":"","RegionGroup":2168}},"AddedSince":"","RequestTypeId":2,"ApiKey":"5f4bc74f-8d9a-41cb-ab85-a1b7cfc86622","SortColumn":2,"SortDirection":2,"Page":{},"PageSize":20,"endpoint":{{"name":"Search","paramsName":"SearchRequest"}},"params":{{"RegionId":2168}}}}',
					'status':'For Sale'}
sale_agreed_body = {'body':'{{"SearchRequest":{{"IsSaleAgreed":"","IsSold":false,"IsAuction":"","UseFreeTextSearchForKeywords":false,"SearchContent":false,"Query":"","PropertyIds":[],"GroupIds":[],"ChannelIds":[1],"PropertyTypeIds":[],"PropertyClassIds":[1],"PropertyStatusIds":[3],"SaleTypeIds":[],"RegionId":"2168","LocalityIds":[],"NegotiatorIds":[],"EnergyRatings":[],"Destinations":[],"MinEnergyRating":"","MaxEnergyRating":"","MinPrice":"","MaxPrice":"","MinBeds":"","MaxBeds":"","MinBathrooms":"","MinSize":"","MaxSize":"","PreSixtyThree":false,"SortBy":"Most Recent","PropertyClassId":"","RegionGroup":2168}},"AddedSince":"","RequestTypeId":2,"ApiKey":"5f4bc74f-8d9a-41cb-ab85-a1b7cfc86622","SortColumn":2,"SortDirection":2,"Page":{},"PageSize":20,"endpoint":{{"name":"Search","paramsName":"SearchRequest"}},"params":{{"RegionId":2168}}}}',
						 'status':'Sale Agreed'}

sold_body = {'body':'{{"SearchRequest":{{"IsSaleAgreed":"","IsSold":false,"IsAuction":"","UseFreeTextSearchForKeywords":false,"SearchContent":false,"Query":"","PropertyIds":[],"GroupIds":[],"ChannelIds":[1],"PropertyTypeIds":[],"PropertyClassIds":[1],"PropertyStatusIds":[4],"SaleTypeIds":[],"RegionId":"2168","LocalityIds":[],"NegotiatorIds":[],"EnergyRatings":[],"Destinations":[],"MinEnergyRating":"","MaxEnergyRating":"","MinPrice":"","MaxPrice":"","MinBeds":"","MaxBeds":"","MinBathrooms":"","MinSize":"","MaxSize":"","PreSixtyThree":false,"SortBy":"Most Recent","PropertyClassId":"","RegionGroup":2168}},"AddedSince":"","RequestTypeId":2,"ApiKey":"5f4bc74f-8d9a-41cb-ab85-a1b7cfc86622","SortColumn":2,"SortDirection":2,"Page":{},"PageSize":20,"endpoint":{{"name":"Search","paramsName":"SearchRequest"}},"params":{{"RegionId":2168}}}}',
				 'status':'Sold'}			

search_results = {}

info = [for_sale_body,sale_agreed_body,sold_body]

for elem in info:
	var = []
	pages = 1
	while True:		
		print("Working on page {}".format(pages))
		body = elem['body'].format(pages)
		try:
			r = requests.post(url, headers = headers, data = body)
		except:
			pages += 1
			continue

		if r.status_code == 200:
			print('SUCCESS: {}'.format(r.status_code))
		else:
			print('HMMMM: {}'.format(r.status_code))
			continue
		
		if pages >1:
			try:
				if var[-1]['SearchResults'][0]['PropertyId'] == r.json()['SearchResults'][0]['PropertyId']:
					print("\nTotal {0} properties pages: {1}\n".format(elem['status'],len(var)))
					break
			except:
				pages += 1
				continue
		pages += 1
		var.append(r.json())
		sf.wait(1)

	search_results[elem['status']] = var

#FORMATTING KEYS

frames = []
var = {}
for key in search_results:
	for value in search_results[key]:
		try:
			results = value['SearchResults']
		except:
			print("ERROR")
			continue
		for result in results:
			var = {}
			var['Key'] = result['PropertyId']
			var['Status'] = key
			frames.append(var)


url = "https://api.myhome.ie/brochure/{}?ApiKey=5f4bc74f-8d9a-41cb-ab85-a1b7cfc86622&RequestTypeId=1"

headers = {'Accept':'application/json, text/plain, */*',
			'Accept-Encoding':'gzip, deflate, br',
			'Host':'api.myhome.ie',
			'Origin':'https://www.myhome.ie'
			}

#REQUESTING EACH PROPERTY KEY

results = []
count = 0
for elem in frames:
	print("Working on {0} of {1}".format(count+1, len(frames)))
	count+=1
	temp = url.format(elem['Key'])
	print("URL: {}".format(temp))
	r = requests.get(temp, headers = headers)
	if r.status_code == 200:
		print('SUCCESS: {}'.format(r.status_code))
	else:
		print('HMMMM: {}'.format(r.status_code))
		continue

	if count%100 == 0:
		print(r.json())
	result = r.json()
	result['STATUS'] = elem['Status']
	results.append(result)

final_file_json = {'results':results}
with open('my_home.json', 'w') as outfile:
    json.dump(final_file_json, outfile)

final_file_csv = json_normalize(results)
final_file_csv.to_csv('my_home.csv',index = False)



