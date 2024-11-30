from typing import Union
import whisper_timestamped as whisper
from whisper import Whisper


class whisper_local:
	model: Union[Whisper, None] = None

	@classmethod
	def initialize_client(cls):
		if cls.model is None:
			m = whisper.load_model("large-v3-turbo")
			assert isinstance(m, Whisper)
			cls.model = m

	@classmethod
	def getTranscript(cls, audio_path: str, prompt='') -> dict:
		cls.initialize_client()
		assert cls.model is not None

		audio = whisper.load_audio(audio_path)

		result = whisper.transcribe_timestamped(cls.model,
		                                        audio,
		                                        language="en",
		                                        initial_prompt=prompt)

		return result
