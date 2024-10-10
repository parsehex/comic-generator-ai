import base64
from PIL import Image
from io import BytesIO
from IPython import display


def saveB64Image(b64, path):
	img = Image.open(BytesIO(base64.b64decode(b64)))
	img.save(path)


def displayB64Image(b64):
	img = display.Image(base64.b64decode(b64), retina=True)
	display.display(img)


def displayText(string):
	htmlstr = ''
	for line in string.split('\n'):
		htmlstr += f'<p>{line}</p>'

	display.display(display.HTML(htmlstr))


def extractSingleJsonString(json: str, key):
	# json is a string output from llm, it may not be valid json
	# carefully try to extract the key's value

	# first, find the key itself, then the next colon
	# then find the next quote to begin the value
	# then find the next quote to end the value
	# return the value

	# find the key
	key_start = json.find(f'"{key}"')
	if key_start == -1:
		print(f'Key "{key}" not found in json')
		return None

	# find the colon
	colon = json.find(':', key_start)
	if colon == -1:
		print(f'Colon not found after key "{key}"')
		return None

	# find the first quote
	first_quote = json.find('"', colon)
	if first_quote == -1:
		print(f'First quote not found after colon')
		return None

	# now, there might not be a closing quote
	# find the next quote
	second_quote = json.find('"', first_quote + 1)
	if second_quote == -1:
		# what is the last character?
		last_char = json[-1]
		is_punctuation = last_char in ['.', '!', '?']
		if is_punctuation:
			# end the string here
			second_quote = len(json) - 1
		else:
			print(f'Second quote not found after first quote')
			return None

	# extract the value
	value = json[first_quote + 1:second_quote]
	return value


def extractSingleArray(json: str, key: str):
	# this is different but similar
	# keep track of values
	# find the key and colon, then the next opening bracket
	# add values as strings between commas
	# stop at the closing bracket
	# return the values

	# remove "```" from the beginning and end
	json = json.strip()
	if json.startswith("```"):
		json = json[3:]
	if json.endswith("```"):
		json = json[:-3]

	# find the key
	key_start = json.find(f'"{key}"')
	if key_start == -1:
		print(f'Key "{key}" not found in json')
		return None

	# find the colon
	colon = json.find(':', key_start)
	if colon == -1:
		print(f'Colon not found after key "{key}"')
		return None

	# find the first bracket
	first_bracket = json.find('[', colon)
	if first_bracket == -1:
		print(f'First bracket not found after colon')
		return None

	# find the last bracket
	last_bracket = json.find(']', first_bracket)
	if last_bracket == -1:
		print(f'Last bracket not found after first bracket')
		return None

	# extract the values
	arr_str = '[' + json[first_bracket + 1:last_bracket] + ']'
	import json
	arr = json.loads(arr_str)
	return arr
