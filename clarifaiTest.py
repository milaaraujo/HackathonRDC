from clarifai.rest import ClarifaiApp
from clarifai.rest import Image as ClImage
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

	app = ClarifaiApp(api_key=options.key)
	model = app.public_models.general_model
	model.model_version = 'aa7f35c01e0642fda5cf400f543e7c40'

	output = open(options.input + '/' + 'outputClarifai.txt', 'w')
	output.writelines('image\tconcepts\n')

	for image in os.listdir(options.input):
		if image.endswith(".jpg"): 
			image_path = os.path.join(options.input, image)
			response = model.predict_by_filename(image_path)

			concepts = []
			for concept in response['outputs'][0]['data']['concepts']:
				concepts.append(concept['name'] + ':' + str(concept['value']))
			concepts = (',').join(concepts)

			output.writelines(image + '\t' + concepts + '\n')
			continue
		else:
			continue

if __name__ == "__main__":
    main()