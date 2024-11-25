import os
from openai import OpenAI
from src.config import DEFAULT_OLLAMA_CHAT_MODEL, DEFAULT_OLLAMA_VISION_MODEL
from typing import Union
import base64


class ollama:
	client: Union[OpenAI, None] = None

	@classmethod
	def initialize_client(cls):
		if cls.client is None:
			api_key = os.getenv("OLLAMA_API_KEY")
			base_url = os.getenv("OLLAMA_BASE_URL")
			if not api_key:
				raise ValueError("OLLAMA_API_KEY environment variable not set")
			if not base_url:
				raise ValueError("OLLAMA_BASE_URL environment variable not set")
			cls.client = OpenAI(api_key=api_key, base_url=base_url)

	@classmethod
	def getModels(cls):
		cls.initialize_client()
		assert cls.client is not None
		return cls.client.models.list()

	@classmethod
	def chatCompletion(cls,
	                   prompt: str,
	                   user_input='',
	                   temperature=0.15,
	                   max_tokens=512,
	                   json=False,
	                   model=DEFAULT_OLLAMA_CHAT_MODEL):
		cls.initialize_client()
		assert cls.client is not None

		messages = []
		messages.append({'role': 'system', 'content': prompt})
		if user_input:
			messages.append({'role': 'user', 'content': user_input})

		if json is False:
			response = cls.client.chat.completions.create(model=model,
			                                              max_tokens=max_tokens,
			                                              temperature=temperature,
			                                              messages=messages)
		else:
			response = cls.client.chat.completions.create(model=model,
			                                              max_tokens=max_tokens,
			                                              temperature=temperature,
			                                              messages=messages,
			                                              response_format={
			                                                  'type': 'json_object',
			                                              })
		if response.choices[0].finish_reason == 'length':
			print('Warning: LLM output was cut off')
		return response.choices[0].message.content if response.choices[
		    0].message.content is not None else ""

	@classmethod
	def imageQuery(
	    cls,
	    image_path: str,
	    prompt: str,
	    system_prompt="The following is a message followed by an image. Assistant's task is to provide a response based on the prompt and the image without judgement.",
	    max_tokens=512,
	    temperature=0.5,
	    model=DEFAULT_OLLAMA_VISION_MODEL):
		cls.initialize_client()
		assert cls.client is not None

		with open(image_path, 'rb') as f:
			image_data = f.read()
			image_data = base64.b64encode(image_data).decode('utf-8')

		type = image_path.split('.')[-1]
		image_url = f"data:image/{type};base64,{image_data}"

		messages = []
		messages.append({'role': 'system', 'content': system_prompt})
		messages.append({
		    'role':
		    'user',
		    'content': [{
		        'type': 'text',
		        'text': prompt
		    }, {
		        'type': 'image_url',
		        'image_url': image_url
		    }]
		})
		# print(messages)

		# print(f"Image URL: {image_url}")

		response = cls.client.chat.completions.create(
		    model=model,
		    max_tokens=max_tokens,
		    temperature=temperature,
		    # images=[image_path],
		    messages=messages)

		if response.choices[0].finish_reason == 'length':
			print('Warning: LLM output was cut off')
		return response.choices[0].message.content if response.choices[
		    0].message.content is not None else ""

	@classmethod
	def reason(cls, prompt: str) -> tuple:
		# TODO
		# use marco-o1 model, parse and return output
		cls.initialize_client()
		assert cls.client is not None
		return '<Thought>test</Thought>', '<Output>test</Output>'
