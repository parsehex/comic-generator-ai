import os
import requests
from src.config import DEFAULT_IMAGE_MODEL


class together:
	baseurl = 'https://api.together.xyz/v1'
	headers = {'Authorization': f'Bearer {os.getenv("TOGETHER_API_KEY")}'}

	@classmethod
	def generateImage(self,
	                  prompt: str,
	                  steps: int,
	                  width=896,
	                  height=1152,
	                  model=DEFAULT_IMAGE_MODEL):
		response = requests.post(f'{self.baseurl}/images/generations',
		                         json={
		                             'prompt': prompt,
		                             'width': width,
		                             'height': height,
		                             'steps': steps,
		                             'model': model,
		                             'n': 1,
		                             'response_format': 'b64_json'
		                         },
		                         headers=self.headers)
		return response.data[0].b64_json
