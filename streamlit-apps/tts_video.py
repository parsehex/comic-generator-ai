import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import streamlit as st
import pandas as pd
import os
import yt_dlp
import ffmpeg
from src.utils import ensuredir, get_text_from_url
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


def process_video_input(input_video):
	"""Process video file or YouTube URL and return path to MP4 file"""
	p = 'output/tmp-video/'
	ensuredir(p)

	if input_video.startswith('http'):  # YouTube URL
		ydl = yt_dlp.YoutubeDL({
		    'outtmpl': f'{p}/%(id)s.%(ext)s',
		})
		ydl.download([input_video])
		video_path = ydl.prepare_filename(
		    ydl.extract_info(input_video, download=False))
	else:  # Local video file
		video_path = input_video

	# Convert to mp4
	output_path = f"{os.path.splitext(video_path)[0]}.mp4"
	ffmpeg.input(video_path).output(output_path).run(overwrite_output=True)
	return output_path


def main():
	st.title("Captioned Video Generator")
	tab1, tab2 = st.tabs(["Generate", "History"])

	with tab1:
		# Sidebar settings
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

		# Main content area
		st.header("Input")
		input_method = st.radio(
		    "Choose input method",
		    ["Text", "File Upload", "URL", "Video File", "YouTube URL"])

		input_src = ''
		input_type = 'text'
		reformat_url_text = False
		is_video_input = False

		if input_method == "Text":
			input_src = st.text_area("Enter your text")
			input_type = 'text'
		elif input_method == "File Upload":
			uploaded_file = st.file_uploader("Upload a file",
			                                 type=['txt', 'mp4', 'mov', 'avi'])
			if uploaded_file:
				if uploaded_file.type.startswith('video/'):
					is_video_input = True
					# Save uploaded video to temporary file
					temp_path = f"output/tmp-video/{uploaded_file.name}"
					ensuredir(temp_path)
					with open(temp_path, "wb") as f:
						f.write(uploaded_file.getbuffer())
					input_src = temp_path
				else:
					input_src = uploaded_file.getvalue().decode()
					input_type = 'text'
		elif input_method == "URL":
			input_src = st.text_input("Enter URL", placeholder="https://example.com")
			reformat_url_text = st.checkbox("Format scraped text using LLM",
			                                value=False)
			input_type = 'url'
		elif input_method == "Video File":
			uploaded_file = st.file_uploader("Upload a video file",
			                                 type=['mp4', 'mov', 'avi'])
			if uploaded_file:
				is_video_input = True
				temp_path = f"output/tmp-video/{uploaded_file.name}"
				ensuredir(temp_path)
				with open(temp_path, "wb") as f:
					f.write(uploaded_file.getbuffer())
				input_src = temp_path
		else:  # YouTube URL
			input_src = st.text_input("Enter YouTube URL")
			if input_src:
				is_video_input = True

		title = st.text_input("Title (optional)",
		                      placeholder="Enter a title for the video")

		if st.button("Generate Video"):
			if input_src:
				with st.spinner("Processing..."):
					try:
						if title:
							input_filename = title.replace(' ', '_')
						elif input_type == 'url':
							input_filename = input_src.split('/')[-1].split('?')[0]
						else:
							f = input_src.split(' ')[:5]
							f = ["".join(e for e in s if e.isalnum()) for s in f]
							input_filename = '_'.join(f)

						if is_video_input:
							# Process video input
							media_path = process_video_input(input_src)
						else:
							# Process text input
							output_file = f'output/tts/{input_filename}.mp3'
							# media_path = make_tts(input_src,
							#                       input_type,
							#                       output_file,
							#                       reformat_url_text=reformat_url_text,
							#                       model=tts_model,
							#                       voice=tts_voice)
							media_path = make_tts(input_src,
							                      input_type,
							                      output_file,
							                      reformat_url_text=reformat_url_text)

						# Create transcript and add subtitles
						srt_file = create_transcript(media_path)
						video_output_file = f"output/video/{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}.mp4"
						ensuredir(video_output_file)

						create_video_with_subtitles(media_path, srt_file,
						                            video_output_file, greenscreen)

						# Add to history
						st.session_state.generated_videos.append({
						    'path':
						    video_output_file,
						    'timestamp':
						    pd.Timestamp.now(),
						    'settings': {
						        'input': input_src,
						        'model': tts_model if not is_video_input else None,
						        'voice': tts_voice if not is_video_input else None,
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
		# History view
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
