import base64
import json
import os
from datetime import datetime
from PIL import Image
from io import BytesIO
from IPython import display
from src.ai import elevenlabs
from newspaper import Article


def ensuredir(path):
	# is file? get dirname
	base = os.path.basename(path)
	if '.' in base:
		path = os.path.dirname(path)

	if not os.path.exists(path):
		os.makedirs(path)


def create_audio(text,
                 audio_name='audio.mp3',
                 project_folder=None,
                 model=None,
                 voice=None):
	# TODO use request stitching to improve gaps
	# see https://elevenlabs.io/docs/api-reference/how-to-use-request-stitching
	if project_folder is None:
		project_folder = create_project_folder()

	audio = elevenlabs.getSpeechB64(text, model, voice)
	audio_path = os.path.join(project_folder, audio_name)
	saveB64Audio(audio, audio_path)

	print(f"Audio {audio_name} created successfully in {project_folder}")
	return project_folder, audio_path


def create_project_folder(type='d', reuse=False):
	if type not in ['d', 'dt']:
		raise ValueError('type must be "d" or "dt"')

	if type == 'd':
		timestamp = datetime.now().strftime("%Y%m%d")
	else:
		timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	folder_name = f"project_{timestamp}"

	if reuse:
		exists = False
		files = os.listdir()
		for file in files:
			if file == folder_name:
				folder_name = file
				exists = True
				break
		if not exists:
			os.makedirs(folder_name)
		return folder_name

	i = 0
	while True:
		folder_name = f"project_{timestamp}_{i}"
		try:
			os.makedirs(folder_name)
			break
		except FileExistsError:
			i += 1
	return folder_name


def saveB64Image(b64, path):
	ensuredir(path)
	img = Image.open(BytesIO(base64.b64decode(b64)))
	img.save(path)


def saveB64Audio(b64, path):
	ensuredir(path)
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


def displayAudio(b64='', path=''):
	if b64:
		audio = display.Audio(data=base64.b64decode(b64))
		display.display(audio)
	elif path:
		audio = display.Audio(path)
		display.display(audio)


# notes about the format that this function supports:
# - lines starting with # are considered titles and are separated from the rest of the text
# - lines starting with [ and ending with ] are considered comments and are removed from the text
def chunkTextForTTS(text: str, max_chars=5000) -> list[dict]:
	sections = []
	lines = text.split('\n')
	section = {'type': 'text', 'content': ''}

	# filter out empty lines
	lines = [line for line in lines if line.strip()]

	for line in lines:
		# '--' to start a new chunk
		if line.startswith('--'):
			if section['content']:
				section['content'] = section['content'].strip()
				sections.append(section)
			section = {'type': 'text', 'content': ''}
			continue

		if '[' in line and ']' in line:  # remove comments
			comment_start = line.find('[')
			comment_end = line.find(']')
			comment = line[comment_start:comment_end + 1]
			line = line.replace(comment, '')

		if line.startswith('#'):  # new title
			if section['content']:
				section['content'] = section['content'].strip()
				sections.append(section)
			section = {'type': 'title', 'content': line.lstrip('#').strip()}
			sections.append(section)
			section = {'type': 'text', 'content': ''}
		else:  # new chunk
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


def chunk_text(text, max_length=5000):
	chunks = []
	while len(text) > max_length:
		# Find the nearest ending punctuation before the max_length
		end = text.rfind('.', 0, max_length)
		if end == -1:
			end = text.rfind('!', 0, max_length)
		if end == -1:
			end = text.rfind('?', 0, max_length)
		if end == -1:
			end = text.rfind('\n', 0, max_length)
		if end == -1:
			end = max_length  # If no punctuation is found, chunk at max_length
		chunks.append(text[:end + 1])
		text = text[end + 1:].strip()
	chunks.append(text)
	return chunks


def get_text_from_url(url, cache_file='cache.json'):
	# Check if the cache file exists
	if os.path.exists(cache_file):
		with open(cache_file, 'r') as f:
			cache = json.load(f)
	else:
		cache = {}

	# Check if the URL is in the cache
	if url in cache:
		print(f"Using cached result for {url}")
		return cache[url]

	# If not, download and parse the article
	article = Article(url)
	article.download()
	article.parse()
	text = article.text

	# Save the result to the cache
	cache[url] = text
	with open(cache_file, 'w') as f:
		json.dump(cache, f)

	return text
