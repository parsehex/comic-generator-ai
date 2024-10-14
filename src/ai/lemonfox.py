import os
from openai import OpenAI


class lemonfox:
	client = OpenAI(api_key=os.getenv("LEMONFOX_API_KEY"),
	                base_url="https://api.lemonfox.ai/v1")

	@classmethod
	def getTranscript(self,
	                  audio_path: str,
	                  prompt='',
	                  granularity='segment',
	                  outformat='verbose_json'):
		audio = open(audio_path, 'rb')
		response = self.client.audio.transcriptions.create(
		    # `model` is not actually used by lemonfox
		    model='whisper-1',
		    file=audio,
		    prompt=prompt,
		    timestamp_granularities=[granularity],
		    response_format=outformat,
		    language='en')

		return response


# note on lemonfox about the `prompt` arg for whisper:
# A text to guide the transcript's style or continue a previous audio transcript. The prompt should be in the same language as the audio.
# Examples
# - Prompts can be useful for fixing words or acronyms that the model might get wrong in the audio. For example, the following prompt improves the transcription of the words "NFT" and "DeFi": The transcript is about blockchain technology, including terms like NFTs and DeFi.. Alternately, the prompt can be a simple list of words: NFT, DeFi, DAO, DApp
# - Sometimes the model skips punctuation in the transcript. You can avoid this by using a simple prompt with punctuation: Hello, welcome to the podcast.
# - The model usually skips common filler words. If you want to keep the filler words in your transcript, use a prompt that includes them: Umm, let's see, hmm... Okay, here's what I'm, like, thinking.
