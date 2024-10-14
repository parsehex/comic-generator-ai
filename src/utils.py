import base64
import json
import os
from datetime import datetime
from PIL import Image
from io import BytesIO
from IPython import display


def create_project_folder():
	timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	folder_name = f"project_{timestamp}"
	os.makedirs(folder_name, exist_ok=True)
	return folder_name


def saveB64Image(b64, path):
	img = Image.open(BytesIO(base64.b64decode(b64)))
	img.save(path)


def saveB64Audio(b64, path):
	audio = base64.b64decode(b64)
	with open(path, 'wb') as f:
		f.write(audio)


def displayB64Image(b64):
	img = display.Image(base64.b64decode(b64), retina=True)
	display.display(img)


def displayText(string):
	htmlstr = ''
	for line in string.split('\n'):
		htmlstr += f'<p>{line}</p>'
	display.display(display.HTML(htmlstr))


def displayAudio(b64):
	audio = display.Audio(data=base64.b64decode(b64))
	display.display(audio)


def chunkTextForTTS(text: str, max_chars=5000):
	sections = []
	lines = text.split('\n')
	section = {'type': 'text', 'content': ''}

	# filter out empty lines
	lines = [line for line in lines if line.strip()]

	for line in lines:
		if line.startswith('#'):
			if section['content']:
				sections.append(section)
			section = {'type': 'title', 'content': line.lstrip('#').strip()}
			sections.append(section)
			section = {'type': 'text', 'content': ''}
		else:
			if len(section['content']) + len(line) + 1 > max_chars:
				sections.append(section)
				section = {'type': 'text', 'content': ''}
			section['content'] += line.strip() + '\n'

	if section['content']:
		sections.append(section)

	return sections


def extractSingleJsonString(json: str, key):
	key_start = json.find(f'"{key}"')
	if key_start == -1:
		print(f'Key "{key}" not found in json')
		return None

	colon = json.find(':', key_start)
	if colon == -1:
		print(f'Colon not found after key "{key}"')
		return None

	first_quote = json.find('"', colon)
	if first_quote == -1:
		print(f'First quote not found after colon')
		return None

	second_quote = json.find('"', first_quote + 1)
	if second_quote == -1:
		last_char = json[-1]
		is_punctuation = last_char in ['.', '!', '?']
		if is_punctuation:
			second_quote = len(json) - 1
		else:
			print(f'Second quote not found after first quote')
			return None

	value = json[first_quote + 1:second_quote]
	return value


def extractSingleArray(json_string: str, key: str):
	json_string = json_string.strip()
	if json_string.startswith("```"):
		json_string = json_string[3:]
	if json_string.endswith("```"):
		json_string = json_string[:-3]

	key_start = json_string.find(f'"{key}"')
	if key_start == -1:
		print(f'Key "{key}" not found in json')
		return None

	colon = json_string.find(':', key_start)
	if colon == -1:
		print(f'Colon not found after key "{key}"')
		return None

	first_bracket = json_string.find('[', colon)
	if first_bracket == -1:
		print(f'First bracket not found after colon')
		return None

	last_bracket = json_string.find(']', first_bracket)
	if last_bracket == -1:
		print(f'Last bracket not found after first bracket')
		return None

	arr_str = '[' + json_string[first_bracket + 1:last_bracket] + ']'
	arr = json.loads(arr_str)
	return arr
