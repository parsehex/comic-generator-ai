import os
from openai import OpenAI
from src.config import DEFAULT_CHAT_MODEL
from typing import Union


class openrouter:
	client: Union[OpenAI, None] = None

	@classmethod
	def initialize_client(cls):
		if cls.client is None:
			api_key = os.getenv("OPENAI_API_KEY")
			if not api_key:
				raise ValueError("OPENAI_API_KEY environment variable not set")
			cls.client = OpenAI(api_key=api_key,
			                    base_url="https://openrouter.ai/api/v1")

	@classmethod
	def chatCompletion(cls,
	                   prompt: str,
	                   user_input='',
	                   temperature=0.15,
	                   max_tokens=512,
	                   json=False,
	                   model=DEFAULT_CHAT_MODEL):
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
