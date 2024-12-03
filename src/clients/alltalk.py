import os
import requests
import json
import httpx
import base64
import typing
from io import BytesIO
from src.config import DEFAULT_TTS_MODEL, DEFAULT_TTS_VOICE
from typing import Union

STREAM_CHUNK_SIZE = 1024


def get_url(url: str) -> str:
	base_url = os.getenv("ALLTALK_BASE_URL")
	if not base_url:
		raise ValueError("ALLTALK_BASE_URL environment variable not set")
	return f"{base_url}{url}"


class alltalk:
	client = None
	headers = {"Accept": "application/json", "Content-Type": "application/json"}

	@classmethod
	def initialize_client(cls):
		if cls.client is None:
			base_url = os.getenv("ALLTALK_BASE_URL")
			if not base_url:
				raise ValueError("ALLTALK_BASE_URL environment variable not set")
			print(f"Initializing AllTalk client with base URL: {base_url}")
			cls.base_url = base_url
			client = requests.Session()
			cls.client = client
			cls.client.headers.update(cls.headers)

	@classmethod
	def getVoices(cls, ) -> list[dict]:
		cls.initialize_client()
		assert cls.client is not None

		url = '/api/voices'
		response = cls.client.get(get_url(url))
		data = response.json()
		return data['voices']

	@classmethod
	def getModels(cls) -> list[str]:
		cls.initialize_client()
		assert cls.client is not None

		url = '/api/currentsettings'
		response = cls.client.get(get_url(url))
		data = response.json()
		return data['models_available']

	@classmethod
	def getSpeechB64(cls, text: str) -> str:
		cls.initialize_client()
		assert cls.client is not None

		response = cls.client.post(
		    get_url("/api/tts-generate"),
		    data={"text_input": text},
		    headers={"Content-Type": "application/x-www-form-urlencoded"})

		if response.ok:
			data = response.json()
			if data['status'] != 'generate-success':
				print('tts failed: ' + response.text)
				return ''
			output_url_path = data['output_file_url']
			response = cls.client.get(get_url(output_url_path))
			audio_base64 = base64.b64encode(response.content).decode('utf-8')
			return audio_base64
		else:
			print('tts failed: ' + response.text)
			return ''
