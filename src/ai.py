import os
import yaml
from openai import OpenAI
from together import Together

config_path = os.path.realpath(
    os.path.join(os.path.dirname(__file__), '../config/config.yaml'))

with open(config_path, 'r') as file:
	config = yaml.safe_load(file)

DEFAULT_CHAT_MODEL = config['ai']['default_chat_model']
DEFAULT_IMAGE_MODEL = config['ai']['default_image_model']

together_client = Together(api_key=os.getenv('TOGETHER_API_KEY'))
openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENAI_API_KEY"),
)


def generateImage(prompt: str,
                  steps: int,
                  width=896,
                  height=1152,
                  model=DEFAULT_IMAGE_MODEL):
	response = together_client.images.generate(prompt=prompt,
	                                           width=width,
	                                           height=height,
	                                           steps=steps,
	                                           model=model,
	                                           n=1,
	                                           response_format='b64_json')
	return response.data[0].b64_json


def chatCompletion(prompt: str,
                   temperature=0.15,
                   max_tokens=512,
                   json=False,
                   model=DEFAULT_CHAT_MODEL):
	if json is False:
		response = openrouter_client.chat.completions.create(
		    model=model,
		    max_tokens=max_tokens,
		    temperature=temperature,
		    messages=[{
		        'role': 'system',
		        'content': prompt
		    }])
	else:
		response = openrouter_client.chat.completions.create(
		    model=model,
		    max_tokens=max_tokens,
		    temperature=temperature,
		    messages=[{
		        'role': 'system',
		        'content': prompt
		    }],
		    response_format={
		        'type': 'json_object',
		    })
	if response.choices[0].finish_reason == 'length':
		print('Warning: LLM output was cut off')
	return response.choices[0].message.content
