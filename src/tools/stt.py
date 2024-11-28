import os
from src.clients import lemonfox
from src.utils import ensuredir
from datetime import datetime


# TODO allow specifying provider
def create_transcript(audio_path: str, type='srt'):
	if type == 'srt':
		return create_transcript_srt(audio_path)
	elif type == 'vjson':
		return create_transcript_vjson(audio_path)
	else:
		raise ValueError('Unsupported type:', type)


def create_transcript_srt(audio_path: str):
	if not os.path.exists(audio_path):
		raise FileNotFoundError('File not found:', audio_path)

	project_folder = 'output/srt'

	# improve transcription by providing a prompt
	whisper_prompt = 'Output the transcript in SRT format using natural prose, with at most 1 sentence per line.'
	transcript_srt = lemonfox.getTranscript(audio_path,
	                                        outformat='srt',
	                                        prompt=whisper_prompt)

	if transcript_srt.startswith('"'):
		transcript_srt = transcript_srt[1:]
	if transcript_srt.endswith('"'):
		transcript_srt = transcript_srt[:-1]
	transcript_srt = transcript_srt.replace('\\n', '\n')
	transcript_srt = transcript_srt.strip()

	transcript_srt_path = os.path.join(
	    project_folder,
	    f'transcript_{datetime.now().strftime("%Y%m%d%H%M%S")}.srt')
	ensuredir(transcript_srt_path)
	with open(transcript_srt_path, 'w') as f:
		f.write(transcript_srt)

	print('Transcript saved to', transcript_srt_path)
	return transcript_srt_path


def create_transcript_vjson(audio_path: str):
	if not os.path.exists(audio_path):
		raise FileNotFoundError('File not found:', audio_path)

	project_folder = 'output/srt'

	transcript_json = lemonfox.getTranscript(audio_path,
	                                         outformat='verbose_json')

	transcript_srt_path = os.path.join(
	    project_folder,
	    f'transcript_{datetime.now().strftime("%Y%m%d%H%M%S")}.json')
	ensuredir(transcript_srt_path)
	with open(transcript_srt_path, 'w') as f:
		f.write(transcript_json)

	print('Transcript saved to', transcript_srt_path)
	return transcript_srt_path
