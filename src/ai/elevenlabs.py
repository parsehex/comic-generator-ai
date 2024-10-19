import os
import requests
import base64
from io import BytesIO
from elevenlabs import ElevenLabs, Model
from src.config import DEFAULT_TTS_MODEL, DEFAULT_TTS_VOICE
from typing import Union

STREAM_CHUNK_SIZE = 1024


class elevenlabs:
	client: Union[ElevenLabs, None] = None
	base_url = "https://api.elevenlabs.io/v1"

	headers = {
	    "Accept": "application/json",
	    "xi-api-key": '',
	    "Content-Type": "application/json"
	}

	@classmethod
	def initialize_client(cls):
		if cls.client is None:
			api_key = os.getenv("ELEVENLABS_API_KEY")
			if not api_key:
				raise ValueError("ELEVENLABS_API_KEY environment variable not set")
			cls.client = ElevenLabs(api_key=api_key)
			cls.headers['xi-api-key'] = api_key

	@classmethod
	def getVoices(cls, ) -> list[dict]:
		cls.initialize_client()
		assert cls.client is not None

		url = f"{cls.base_url}/voices"
		response = requests.get(url, headers=cls.headers)
		data = response.json()
		return data['voices']

	@classmethod
	def getModels(cls) -> list[Model]:
		cls.initialize_client()
		assert cls.client is not None

		data = cls.client.models.get_all()
		return data

	@classmethod
	def getSpeechB64(cls,
	                 text: str,
	                 model_id=DEFAULT_TTS_MODEL,
	                 voice_id=DEFAULT_TTS_VOICE,
	                 outformat='mp3_22050_32') -> str:
		cls.initialize_client()

		url = f"{cls.base_url}/text-to-speech/{voice_id}/stream"

		data = {
		    "text": text,
		    "model_id": model_id,
		    'output_format': outformat,
		    "voice_settings": {
		        "stability": 0.5,
		        "similarity_boost": 0.8,
		        "style": 0.0,
		        "use_speaker_boost": True
		    }
		}

		response = requests.post(url, headers=cls.headers, json=data, stream=True)

		if response.ok:
			audio_stream = BytesIO()
			for chunk in response.iter_content(chunk_size=STREAM_CHUNK_SIZE):
				audio_stream.write(chunk)
			audio_content = audio_stream.getvalue()
			audio_base64 = base64.b64encode(audio_content).decode('utf-8')
			return audio_base64
		else:
			print(response.text)
			return ''

	@classmethod
	def getSoundEffectB64(cls,
	                      prompt: str,
	                      duration_seconds=None,
	                      prompt_influence=0.3) -> str:
		url = f"{cls.base_url}/sound-generation"

		data = {
		    "text": prompt,
		    "duration_seconds": duration_seconds,
		    "prompt_influence": prompt_influence
		}

		response = requests.post(url, headers=cls.headers, json=data, stream=True)

		if response.ok:
			audio_stream = BytesIO()
			for chunk in response.iter_content(chunk_size=STREAM_CHUNK_SIZE):
				audio_stream.write(chunk)
			audio_content = audio_stream.getvalue()
			audio_base64 = base64.b64encode(audio_content).decode('utf-8')
			return audio_base64
		else:
			print(response.text)
			return ''
