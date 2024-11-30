import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import os
from src.utils import ensuredir, displayVideo
from src.enums import ElevenLabsTTSModel, ElevenLabsTTSVoice
from src.tools.tts import make_tts
from src.tools.stt import create_transcript
from src.video.moviepy import create_video_with_subtitles

# change the model and/or voice if desired
# TODO support openai tts
tts_model = ElevenLabsTTSModel.Multilingual_v2.value
tts_voice = ElevenLabsTTSVoice.Brian.value  # TODO add more voices to enum

# choose 1 of the below inputs
input_text = ""
input_file = ''
input_url = 'http://example.com'
reformat_url_text = True

# optionally save the audio
output_file = 'test1.mp3'

input_type = 'text'
input_src = input_text
if input_file:
	input_type = 'file'
	input_src = input_file
elif input_url:
	input_type = 'url'
	input_src = input_url

audio = make_tts(input_src,
                 input_type,
                 output_file,
                 model=tts_model,
                 voice=tts_voice)

# Generate SRT file
srt_file = create_transcript(audio)  # Your existing function

# Create video with subtitles
video_output_file = f"{os.path.splitext(audio)[0]}.mp4"
# save in output/video
video_output_file = video_output_file.replace('tts', 'video')
ensuredir(video_output_file)
create_video_with_subtitles(audio, srt_file, video_output_file, False)
print(f'Video saved to {video_output_file}')
displayVideo(path=video_output_file)

# displayAudio(audio)
