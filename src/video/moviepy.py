from moviepy.editor import AudioFileClip, TextClip, CompositeVideoClip
from moviepy.video.VideoClip import ColorClip
from moviepy.editor import VideoFileClip


def create_video_with_subtitles(media_file,
                                srt_file,
                                output_video_file,
                                greenscreen=True):
	# Determine if the input is an audio or video file
	if media_file.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
		media_clip = VideoFileClip(media_file)
	else:
		media_clip = AudioFileClip(media_file)
	duration = media_clip.duration

	# Read and parse the SRT file
	with open(srt_file, 'r', encoding='utf-8') as f:
		srt_content = f.read().strip().split('\n\n')

	bg_color = (0, 0, 0)
	if greenscreen:
		bg_color = (0, 255, 0)

	# Create subtitle clips
	subtitle_clips = []
	for block in srt_content:
		parts = block.split('\n')
		if len(parts) >= 3:  # Ensure proper SRT format
			times = parts[1].split(' --> ')
			start_time = sum(
			    float(x) * 60**i for i, x in enumerate(
			        reversed(times[0].replace(',', '.').split(':'))))
			end_time = sum(
			    float(x) * 60**i for i, x in enumerate(
			        reversed(times[1].replace(',', '.').split(':'))))
			text = ' '.join(parts[2:])

			txt_clip = (TextClip(
			    text,
			    fontsize=24,
			    color='white',
			    stroke_color='rgb(50, 50, 50)',
			    stroke_width=1,
			    bg_color=f'rgb{bg_color}',
			    size=(720, None),
			    method='caption').set_start(start_time).set_duration(
			        end_time - start_time).set_position(('center', 'bottom')))
			subtitle_clips.append(txt_clip)

	# Create a background clip if the input is an audio file
	if isinstance(media_clip, AudioFileClip):
		background_clip = ColorClip(size=(720, 480),
		                            color=bg_color,
		                            duration=duration)
		final_clip = CompositeVideoClip([background_clip] + subtitle_clips)
	else:
		final_clip = CompositeVideoClip([media_clip] + subtitle_clips)

	audio: AudioFileClip
	if isinstance(media_clip, AudioFileClip):
		audio = media_clip
	elif media_clip.audio is not None:
		audio = media_clip.audio
	final_clip = final_clip.set_audio(audio)

	# Write the final video
	final_clip.write_videofile(output_video_file, fps=24)

	# Clean up
	media_clip.close()
	final_clip.close()


def create_video_from_audio(audio_file, output_video_file):
	"""
	Create a video with a black background and the audio from the input file.
	"""
	# Load the audio file
	audio_clip = AudioFileClip(audio_file)
	duration = audio_clip.duration

	# Create a background clip
	background_clip = ColorClip(size=(720, 480),
	                            color=(0, 0, 0),
	                            duration=duration)

	# Combine all clips
	final_clip = CompositeVideoClip([background_clip])
	final_clip = final_clip.set_audio(audio_clip)

	# Write the final video
	final_clip.write_videofile(output_video_file, fps=24)

	# Clean up
	audio_clip.close()
	final_clip.close()
