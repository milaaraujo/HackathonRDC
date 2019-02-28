import requests
import os.path
from clarifai.rest import ClarifaiApp
from clarifai.rest import Image as ClImage
from optparse import OptionParser
import getopt, sys, os
import json
import time

def main():

	parser = OptionParser("")
	parser.add_option("-i", dest="input", type="string", help="Input folder")
	parser.add_option("-o", dest="output", type="string", help="Output folder")
	parser.add_option("-a", dest="key1", type="string", help="Azure subscription key")
	parser.add_option("-c", dest="key2", type="string", help="Clarifai subscription key")

	(options, args) = parser.parse_args()
	
	if options.key1 is None:
		print "Missing subscription key.\n"
		exit(-1)
	if options.key2 is None:
		print "Missing subscription key.\n"
		exit(-1)					
	if options.input is None:
		print "Missing input folder.\n"
		exit(-1)		
	if options.output is None:
		parser.error("Missing output folder .\n")
		exit(-1)

	azure_subscription_key = options.key1
	assert azure_subscription_key

	vision_base_url = "https://westcentralus.api.cognitive.microsoft.com/vision/v2.0/"
	analyze_url = vision_base_url + "analyze"

	app = ClarifaiApp(api_key=options.key2)
	model = app.public_models.general_model
	model.model_version = 'aa7f35c01e0642fda5cf400f543e7c40'

	roomTypes = {
		' basement ',
		' bathroom ',
		' bedroom ',
		' den ',
		' dining ',
		' exercise room ',
		' family room ',
		' game room ',
		' great room ',
		' gym ',
		' kitchen ',
		' laundry ',
		' library ',
		' living room ',
		' loft ',
		' media room ',
		' office ',
		' sauna ',
		' workshop '
	}

	row_id = 0
	record = []

	for folder in os.listdir(options.input):
		if os.path.isdir(options.input + folder):

			listing = folder
			folder = options.input + folder + '/'

			fields = []
			fields.append({'field':'SourceListingID', 'value':listing})
			roomCount = {}

			for image in os.listdir(folder):
				if image.endswith(".jpg"): 

					image_path = os.path.join(folder, image)

					################### Azure
					image_data = open(image_path, "rb").read()
					headers    = {'Ocp-Apim-Subscription-Key': azure_subscription_key,
			              		  'Content-Type': 'application/octet-stream'}
					params     = {'visualFeatures': 'Categories,Description,Tags'}
					response = requests.post(
			    			analyze_url, headers=headers, params=params, data=image_data)
					response.raise_for_status()

					analysis = response.json()

					if analysis["description"]["captions"]:
						description = analysis["description"]["captions"][0]["text"].capitalize()
					else:
						description = ''


					room = 'noroom'	
					for item in roomTypes:
						if item in description:
							room = item.strip()
							break
							
					####################### Clarifai
					response = model.predict_by_filename(image_path)

					concepts = []
					for concept in response['outputs'][0]['data']['concepts']:
						if float(concept['value']) > 0.90:
							concepts.append(concept['name'])
					concepts = (',').join(concepts)

					if room in roomCount:
						roomCount[room] += 1
					else:
						roomCount[room] = 0

					fields.append({'field':'clarifai_' + room + '_' + str(roomCount[room]), 'value':concepts})

					print 'Done with photo: ' + image

					#Avoiding 'Too Many Requests'
					#time.sleep(5)

					continue
				else:
					continue
            
			record.append({
				'row_id' : row_id,
				'data' : fields
			})
			row_id += 1
			print 'Done with listing: ' + listing

			#Avoiding 'Too Many Requests'
			#time.sleep(10)			


	with open(options.input + '/' + 'output.json', 'w') as outfile:
		json.dump({'entity' : record}, outfile)


if __name__ == "__main__":
    main()