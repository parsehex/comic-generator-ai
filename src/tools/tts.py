# def make_tts():
# params:
# - input_src: str
# - input_type: str
# - reformat_url_text = False
# - model = ElevenLabsTTSModel.Multilingual_v2.value
# - voice = ElevenLabsTTSVoice.Brian.value

# let me think here, how do we want to handle different models/providers?

from typing import Union, Literal, Optional, Dict, Any
from pathlib import Path
from src.clients import elevenlabs
from src.enums import ElevenLabsTTSModel, ElevenLabsTTSVoice
from src.format_tts import format_tts_text
from src.utils import get_text_from_url, chunk_text, saveB64Audio
from pydub import AudioSegment

InputType = Literal["text", "file", "url"]

CHUNK_LENGTH = 5000


# TODO: allow specifying provider
def make_tts(input_src: Union[str, Path],
             input_type: InputType,
             output_path: str = 'output/tts/output.mp3',
             reformat_url_text=False,
             model: str = ElevenLabsTTSModel.Multilingual_v2.value,
             voice: str = ElevenLabsTTSVoice.Brian.value):
	input_text: str = ''
	if input_type == 'text':
		input_text = str(input_src)
	elif input_type == 'file':
		input_text = Path(input_src).read_text()
	elif input_type == 'url':
		res = get_text_from_url(input_src)
		if reformat_url_text:
			res = format_tts_text(input_text)
		input_text = res

	chunks = []
	if len(input_text) > CHUNK_LENGTH:
		chunks = chunk_text(input_text, CHUNK_LENGTH)
	else:
		chunks.append(input_text)
	has_multiple_chunks = len(chunks) > 1

	audio_segments = []

	if has_multiple_chunks:
		for i, chunk in enumerate(chunks):
			previous_text = ' '.join(chunks[:i])
			next_text = ' '.join(chunks[i + 1:])
			chunk_path = f"{output_path}_{i}.mp3"
			o = get_speech_as_file(chunk, chunk_path, model, voice, previous_text,
			                       next_text)
			chunk_path = o['path']
			audio_segments.append(AudioSegment.from_file(chunk_path, format="mp3"))

		# combine all the chunks
		combined = audio_segments[0]
		for segment in audio_segments[1:]:
			combined += segment
		combined.export(output_path, format="mp3")

		# delete the chunks
		for i in range(len(chunks)):
			Path(f"{output_path}_{i}.mp3").unlink()
	else:
		o = get_speech_as_file(input_text, output_path, model, voice)
		output_path = o['path']

	return output_path


def get_speech_as_file(
    input_text: str,
    output_path: str,
    previous_text: Optional[str] = None,
    next_text: Optional[str] = None,
    model: str = ElevenLabsTTSModel.Multilingual_v2.value,
    voice: str = ElevenLabsTTSVoice.Brian.value) -> Dict[str, Any]:
	if Path(output_path).exists():
		print('File already exists:', output_path)
		return {'path': output_path}

	# get the audio
	tts = elevenlabs.getSpeechB64(input_text,
	                              model_id=model,
	                              voice_id=voice,
	                              previous_text=previous_text,
	                              next_text=next_text)
	saveB64Audio(tts, output_path)
	return {'path': output_path}
