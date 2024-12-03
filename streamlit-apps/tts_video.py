import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
import pandas as pd
import os
from src.utils import ensuredir
from src.enums import ElevenLabsTTSModel, ElevenLabsTTSVoice
from src.tools.format_tts import format_tts_text
from src.tools.tts import make_tts
from src.tools.stt import create_transcript
from src.video.moviepy import create_video_with_subtitles
from dotenv import load_dotenv

load_dotenv()

# init session state
if 'generated_videos' not in st.session_state:
	st.session_state.generated_videos = []


def main():
	st.title("Video Generator")

	tab1, tab2 = st.tabs(["Generate", "History"])

	with tab1:
		# main generation interface
		with st.sidebar:
			st.header("TTS Settings")
			tts_model = st.selectbox(
			    "Model",
			    options=[model.value for model in ElevenLabsTTSModel],
			    key="tts_model")
			tts_voice = st.selectbox(
			    "Voice",
			    options=[voice.value for voice in ElevenLabsTTSVoice],
			    key="tts_voice")
			st.header("Video Settings")
			greenscreen = st.checkbox("Use green background", value=False)

		# main content area
		st.header("Input")
		input_method = st.radio("Choose input method",
		                        ["Text", "File Upload", "URL"])

		input_src = ''
		input_type = 'text'
		reformat_url_text = False

		if input_method == "Text":
			input_src = st.text_area("Enter your text")
			input_type = 'text'
		elif input_method == "File Upload":
			uploaded_file = st.file_uploader("Upload a text file", type=['txt'])
			if uploaded_file:
				input_src = uploaded_file.getvalue().decode()
				input_type = 'text'
		else:
			input_src = st.text_input("Enter URL",
			                          placeholder="https://example.com",
			                          value="https://example.com")
			reformat_url_text = st.checkbox("Format scraped text using LLM",
			                                value=False)
			input_type = 'url'

		title = st.text_input("Title (optional)",
		                      placeholder="Enter a title for the video")

		if st.button("Generate Video"):
			if input_src:
				with st.spinner("Processing..."):
					try:
						# use either the title, url or the first few words as the filename
						if title:
							input_filename = title.replace(' ', '_')
						elif input_type == 'url':
							input_filename = input_src.split('/')[-1].split('?')[0]
						else:
							input_filename = input_src.split(' ')[:5]
							input_filename = '_'.join(input_filename)
						output_file = f'output/tts/{input_filename}.mp3'
						audio = make_tts(input_src,
						                 input_type,
						                 output_file,
						                 reformat_url_text=reformat_url_text,
						                 model=tts_model,
						                 voice=tts_voice)
						srt_file = create_transcript(audio)
						video_output_file = f"{os.path.splitext(audio)[0]}.mp4"
						# use timestamp for filename
						video_output_file = video_output_file.replace(
						    os.path.basename(video_output_file),
						    f"{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}.mp4")
						video_output_file = video_output_file.replace('tts', 'video')
						ensuredir(video_output_file)

						# Create video
						create_video_with_subtitles(audio, srt_file, video_output_file,
						                            greenscreen)

						# Add to history
						st.session_state.generated_videos.append({
						    'path':
						    video_output_file,
						    'timestamp':
						    pd.Timestamp.now(),
						    'settings': {
						        'input': input_src,
						        'model': tts_model,
						        'voice': tts_voice,
						        'greenscreen': greenscreen
						    }
						})

						# Show result
						st.success("Video generated!")
						st.video(video_output_file)

						# Download button
						filename = os.path.basename(video_output_file)
						with open(video_output_file, 'rb') as f:
							st.download_button("Download Video",
							                   data=f,
							                   file_name=filename,
							                   mime="video/mp4")

					except Exception as e:
						st.error(f"Error: {str(e)}")
			else:
				st.warning("Please provide input")

	with tab2:
		# history view
		st.header("Generation History")
		if st.session_state.generated_videos:
			for video in reversed(st.session_state.generated_videos):
				with st.expander(f"Video from {video['timestamp']}"):
					st.video(video['path'])
					st.json(video['settings'])
		else:
			st.info("No videos generated yet")


if __name__ == "__main__":
	main()
