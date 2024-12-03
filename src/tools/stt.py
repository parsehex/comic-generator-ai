import json, os
from src.clients import lemonfox, whisper_local
from src.utils import ensuredir
from datetime import datetime
import ffmpeg


# TODO allow specifying provider
def create_transcript(media_path: str, type='srt', provider='whisper_local'):
	# if path is a video file, extract audio
	if media_path.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
		audio_path = os.path.join('output', 'audio', 'audio.wav')
		ensuredir(audio_path)
		ffmpeg.input(media_path).output(audio_path).run(overwrite_output=True)
	else:
		audio_path = media_path

	if provider == 'whisper_local':
		srt = False
		if type == 'srt':
			srt = True
		return create_transcript_local(audio_path, srt)

	if type == 'srt':
		return create_transcript_srt(audio_path)
	elif type == 'vjson':
		return create_transcript_vjson(audio_path)
	else:
		raise ValueError('Unsupported type:', type)


def convert_timestamps_to_srt(timestamps: list):
	srt = ''
	for i, ts in enumerate(timestamps):
		srt += f'{i + 1}\n'
		srt += f'{ts["start"]} --> {ts["end"]}\n'
		srt += f'{ts["text"]}\n\n'
	return srt


def create_transcript_local(audio_path: str, srt=False):
	if not os.path.exists(audio_path):
		raise FileNotFoundError('File not found:', audio_path)

	project_folder = 'output/transcripts'

	transcript_json = whisper_local.getTranscript(
	    audio_path,
	    "Transcribe the following audio into text, with 1 sentence per line.")
	transcript_json = json.dumps(transcript_json, indent=4)

	transcript_srt_path = os.path.join(
	    project_folder,
	    f'transcript_{datetime.now().strftime("%Y%m%d%H%M%S")}.json')
	ensuredir(transcript_srt_path)
	with open(transcript_srt_path, 'w') as f:
		f.write(transcript_json)

	if srt:
		transcript_json = json.loads(transcript_json)
		transcript_srt = convert_timestamps_to_srt(transcript_json['segments'])
		transcript_srt_path = os.path.join(
		    project_folder,
		    f'transcript_{datetime.now().strftime("%Y%m%d%H%M%S")}.srt')
		ensuredir(transcript_srt_path)
		with open(transcript_srt_path, 'w') as f:
			f.write(transcript_srt)

	return transcript_srt_path


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
