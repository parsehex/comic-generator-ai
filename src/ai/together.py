import os
from together import Together
from src.config import DEFAULT_IMAGE_MODEL


class together:
	client = Together(api_key=os.getenv('TOGETHER_API_KEY'))

	@classmethod
	def generateImage(self,
	                  prompt: str,
	                  steps: int,
	                  width=896,
	                  height=1152,
	                  model=DEFAULT_IMAGE_MODEL):
		response = self.client.images.generate(prompt=prompt,
		                                       width=width,
		                                       height=height,
		                                       steps=steps,
		                                       model=model,
		                                       n=1,
		                                       response_format='b64_json')
		return response.data[0].b64_json
