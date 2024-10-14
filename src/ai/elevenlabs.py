import os
import requests
import base64
from io import BytesIO
from elevenlabs import ElevenLabs
from src.config import DEFAULT_TTS_MODEL, DEFAULT_TTS_VOICE

STREAM_CHUNK_SIZE = 1024


class elevenlabs:
	client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
	base_url = "https://api.elevenlabs.io/v1"

	headers = {
	    "Accept": "application/json",
	    "xi-api-key": os.getenv("ELEVENLABS_API_KEY"),
	    "Content-Type": "application/json"
	}

	@classmethod
	def getVoices(self, ) -> list[dict]:
		url = f"{self.base_url}/voices"
		response = requests.get(url, headers=self.headers)
		data = response.json()
		return data['voices']

	@classmethod
	def getModels(self, ) -> list[dict]:
		data = self.client.models.get_all()
		return data

	@classmethod
	def getSpeechB64(self,
	                 text: str,
	                 voice_id=DEFAULT_TTS_VOICE,
	                 outformat='mp3_22050_32') -> str:
		url = f"{self.base_url}/text-to-speech/{voice_id}/stream"

		data = {
		    "text": text,
		    "model_id": DEFAULT_TTS_MODEL,
		    'output_format': outformat,
		    "voice_settings": {
		        "stability": 0.5,
		        "similarity_boost": 0.8,
		        "style": 0.0,
		        "use_speaker_boost": True
		    }
		}

		response = requests.post(url, headers=self.headers, json=data, stream=True)

		if response.ok:
			audio_stream = BytesIO()
			for chunk in response.iter_content(chunk_size=STREAM_CHUNK_SIZE):
				audio_stream.write(chunk)
			audio_content = audio_stream.getvalue()
			audio_base64 = base64.b64encode(audio_content).decode('utf-8')
			return audio_base64
		else:
			print(response.text)
			return None
