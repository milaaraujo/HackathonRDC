import requests
import os.path
from optparse import OptionParser
import getopt, sys, os

def main():

	parser = OptionParser("")
	parser.add_option("-i", dest="input", type="string", help="Input folder")
	parser.add_option("-o", dest="output", type="string", help="Output folder")
	parser.add_option("-k", dest="key", type="string", help="Subscription key")

	(options, args) = parser.parse_args()
	
	if options.key is None:
		print "Missing subscription key.\n"
		exit(-1)
	if options.input is None:
		print "Missing input folder.\n"
		exit(-1)		
	if options.output is None:
		parser.error("Missing output folder .\n")
		exit(-1)

	subscription_key = options.key
	assert subscription_key

	vision_base_url = "https://westcentralus.api.cognitive.microsoft.com/vision/v2.0/"
	analyze_url = vision_base_url + "analyze"

	output = open(options.input + '/' + 'outputAzure.txt', 'w')
	output.writelines('image\tdescription\tcategories\ttags\n')

	for image in os.listdir(options.input):
		if image.endswith(".jpg"): 

			image_path = os.path.join(options.input, image)

			image_data = open(image_path, "rb").read()
			headers    = {'Ocp-Apim-Subscription-Key': subscription_key,
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

			categories = []
			for category in analysis['categories']:
				categories.append(category['name'] + ':' + str(category['score']))
			categories = (',').join(categories)

			tags = []
			for tag in analysis["tags"]:
				tags.append(tag['name'] + ':' + str(tag['confidence']))
			tags = (',').join(tags)

			output.writelines(image + '\t' + description + '\t' + categories + '\t' + tags + '\n')

			continue
		else:
			continue

if __name__ == "__main__":
    main()