# comic-generator-ai

This is an attempt to use AI models to generate a comic kind of thing. I think the models are there to do this along with some traditional programming.

I'm making this through a Jupyter notebook at the moment. You can likely check the [`main.ipynb`](main.ipynb) file to see where I am now.

---

I'm finding that I'm using this for various sorts of notebooks. Much of it is media generation using AI or through `moviepy` or `ffmpeg`.

- `main.ipynb` - my initial attempt to make a story with relevant image/comic panels
- `gen_tts.ipynb` - simple notebook to generate some audio from text
- `gen_img.ipynb`
- `tts_chunks.ipynb` - takes in a markdown-ish script and generates TTS from it in chunks -`tts_video.ipynb` and `tts_video_moviepy.ipynb` - an attempt before `tts_chunks.ipynb` to create a video with TTS audio and burned-in subtitles from a script. The former uses `ffmpeg` and the latter uses `moviepy`
- `save_rtspstream.py` - a script to save an RTSP stream to a file
  - A project I want to try is to use a vision model to make a system for controlling/recording security camera feeds.

Instead of `comic-generator-ai`, I need to rename this repo.
