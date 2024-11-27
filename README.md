# Creator Tools

This is a project to generate media using AI models. I started with wanting to make a comic strip generator, but I've found that I'm using this for various sorts of notebooks related to generating media.

## Notebooks

Generally I'm starting with notebooks to prototype ideas and then moving them to scripts once they take shape / become useful.

- `main.ipynb` - my initial attempt to make a story with relevant image/comic panels
- `audio_to_srt.ipynb` - notebook to generate subtitles from an audio file
- `f5_tts.ipynb` - generate TTS using the open source F5 TTS model
- `gen_soundeffects.ipynb` - play/save sound effects from ElevenLabs
- `gen_tts.ipynb` - simple notebook to generate some audio from text
- `gen_img.ipynb`
- `tts_chunks.ipynb` - takes in a markdown-ish script and generates TTS from it in chunks -`tts_video.ipynb` and `tts_video_moviepy.ipynb` - an attempt before `tts_chunks.ipynb` to create a video with TTS audio and burned-in subtitles from a script. The former uses `ffmpeg` and the latter uses `moviepy`

## Scripts

I've started taking notebooks and turning them into scripts for easier use (most using PyQt5 for the GUI).

- `gen_tts_app.py` - simple app to generate audio from text, able to specify model and voice
- `tts_chunks_app.py` - more complex app/interface to generate audio from a script of text
- `save_rtsp_stream.py` - a script to save an RTSP stream to a file
  - A project I want to try is to use a vision model to make a system for controlling/recording security camera feeds.

# License

Copyright 2024 Thomas Mays

Code under the `autocaption/` directory is modified from https://github.com/chigozienri/cog-autocaption and https://github.com/fictions-ai/autocaption

Copyright 2023 Fictions.ai

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
