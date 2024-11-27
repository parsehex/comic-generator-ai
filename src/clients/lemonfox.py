import os
from openai import OpenAI
from typing import Union


class lemonfox:
	client: Union[OpenAI, None] = None

	@classmethod
	def initialize_client(cls):
		if cls.client is None:
			api_key = os.getenv("LEMONFOX_API_KEY")
			if not api_key:
				raise ValueError("LEMONFOX_API_KEY environment variable not set")
			cls.client = OpenAI(api_key=api_key,
			                    base_url="https://api.lemonfox.ai/v1")

	@classmethod
	def getTranscript(cls,
	                  audio_path: str,
	                  prompt='',
	                  granularity='segment',
	                  outformat='verbose_json'):
		cls.initialize_client()
		assert cls.client is not None

		audio = open(audio_path, 'rb')
		response = cls.client.audio.transcriptions.create(
		    # `model` is not actually used by lemonfox
		    model='whisper-1',
		    file=audio,
		    prompt=prompt,
		    timestamp_granularities=[granularity],
		    response_format=outformat,
		    language='en')
		if outformat == 'verbose_json' or outformat == 'json':
			return str(response.model_dump_json())

		return response


# note on lemonfox about the `prompt` arg for whisper:
# A text to guide the transcript's style or continue a previous audio transcript. The prompt should be in the same language as the audio.
# Examples
# - Prompts can be useful for fixing words or acronyms that the model might get wrong in the audio. For example, the following prompt improves the transcription of the words "NFT" and "DeFi": The transcript is about blockchain technology, including terms like NFTs and DeFi.. Alternately, the prompt can be a simple list of words: NFT, DeFi, DAO, DApp
# - Sometimes the model skips punctuation in the transcript. You can avoid this by using a simple prompt with punctuation: Hello, welcome to the podcast.
# - The model usually skips common filler words. If you want to keep the filler words in your transcript, use a prompt that includes them: Umm, let's see, hmm... Okay, here's what I'm, like, thinking.
