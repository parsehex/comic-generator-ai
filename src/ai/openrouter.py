import os
from openai import OpenAI
from src.config import DEFAULT_CHAT_MODEL

openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENAI_API_KEY"),
)


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
