from moviepy.editor import AudioFileClip, TextClip, CompositeVideoClip
from moviepy.video.VideoClip import ColorClip
from moviepy.editor import VideoFileClip


def create_word_clips(text_segment,
                      start_time,
                      end_time,
                      fontsize=24,
                      bg_color=(0, 0, 0, 0),
                      width=720,
                      height=480):
	"""Create clips for full text with word highlighting"""
	words = text_segment.split()
	duration = end_time - start_time
	word_duration = duration / len(words)

	word_clips = []
	line_words = []
	current_line_width = 0
	max_line_width = width - 100  # Leave margins
	lines_info = []

	# First pass: measure words and organize into lines
	current_time = start_time
	current_line = []

	# Create a temp clip to get consistent height
	temp_clip = TextClip(
	    "TEST",
	    fontsize=fontsize,
	    color='white',
	    stroke_color='rgb(50, 50, 50)',
	    stroke_width=1,
	)
	line_height = temp_clip.size[1]

	for word in words:
		word_clip = TextClip(word,
		                     fontsize=fontsize,
		                     color='white',
		                     stroke_color='rgb(50, 50, 50)',
		                     stroke_width=1,
		                     bg_color=f'rgba{bg_color}')

		word_width = word_clip.size[0]

		# Check if adding this word would exceed line width
		if current_line_width + word_width + 10 > max_line_width and current_line:
			# Store current line info
			lines_info.append({
			    'words': current_line,
			    'width': current_line_width,
			    'height': line_height
			})
			# Reset for new line
			current_line = []
			current_line_width = 0

		current_line.append({
		    'word': word,
		    'width': word_width,
		    'start': current_time,
		    'end': current_time + word_duration
		})
		current_line_width += word_width + 10  # Add space between words
		current_time += word_duration

	# Add the last line
	if current_line:
		lines_info.append({
		    'words': current_line,
		    'width': current_line_width,
		    'height': line_height
		})

	# Calculate total height of text block
	total_height = len(lines_info) * (line_height + 5
	                                  )  # 5px spacing between lines

	# Position the entire block from the bottom with margin
	bottom_margin = 40
	start_y = height - bottom_margin - total_height

	# Second pass: create all clips with proper positioning
	current_y = start_y

	for line in lines_info:
		# Center this line
		start_x = (width - line['width']) / 2
		current_x = start_x

		for word_info in line['words']:
			# Base word clip (visible entire duration)
			base_clip = (TextClip(
			    word_info['word'],
			    fontsize=fontsize,
			    color='white',
			    stroke_color='rgba(50, 50, 50, 0)',
			    stroke_width=1,
			    bg_color=f'rgb{bg_color}').set_position(
			        (current_x,
			         current_y)).set_start(start_time).set_duration(end_time -
			                                                        start_time))

			# Highlight clip (visible only during word timing)
			highlight_clip = (
			    TextClip(
			        word_info['word'],
			        fontsize=fontsize,
			        color='yellow',  # Highlight color
			        stroke_color='rgb(50, 50, 50)',
			        stroke_width=1,
			        bg_color=f'rgb{bg_color}').set_position(
			            (current_x, current_y)).set_start(
			                word_info['start']).set_duration(word_info['end'] -
			                                                 word_info['start']))

			word_clips.extend([base_clip, highlight_clip])
			current_x += word_info['width'] + 10  # Add space between words

		current_y += line_height + 5  # Move to next line

	return word_clips, total_height


def create_video_with_subtitles(media_file,
                                srt_file,
                                output_video_file,
                                greenscreen=True,
                                width=720,
                                height=480):
	# Media file handling
	if media_file.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
		media_clip = VideoFileClip(media_file)
	else:
		media_clip = AudioFileClip(media_file)
	duration = media_clip.duration
	if isinstance(media_clip, VideoFileClip):
		width, height = media_clip.size

	# Read and parse the SRT file
	with open(srt_file, 'r', encoding='utf-8') as f:
		srt_content = f.read().strip().split('\n\n')

	bg_color = (0, 255, 0) if greenscreen else (0, 0, 0)

	all_clips = []
	y_offset = 150  # Starting Y position near bottom

	for block in srt_content:
		parts = block.split('\n')
		if len(parts) >= 3:
			times = parts[1].split(' --> ')
			start_time = sum(
			    float(x) * 60**i for i, x in enumerate(
			        reversed(times[0].replace(',', '.').split(':'))))
			end_time = sum(
			    float(x) * 60**i for i, x in enumerate(
			        reversed(times[1].replace(',', '.').split(':'))))
			text = ' '.join(parts[2:])

			# Create word clips with highlighting
			word_clips, height_used = create_word_clips(text,
			                                            start_time,
			                                            end_time,
			                                            fontsize=24,
			                                            bg_color=bg_color,
			                                            width=width,
			                                            height=height)

			# Adjust all clips to the current y_offset
			for clip in word_clips:
				current_pos = clip.pos
				if isinstance(current_pos, tuple):
					clip = clip.set_position((current_pos[0], current_pos[1] + y_offset))
				all_clips.append(clip)

			# Update y_offset for next segment if needed
			y_offset += height_used + 20
			if y_offset > 440:  # Reset if too low
				y_offset = 380

	# Create the final composite
	if isinstance(media_clip, AudioFileClip):
		background_clip = ColorClip(size=(width, height),
		                            color=bg_color,
		                            duration=duration)
		final_clip = CompositeVideoClip([background_clip] + all_clips)
	else:
		final_clip = CompositeVideoClip([media_clip] + all_clips)

	# Set audio and write video
	audio = media_clip if isinstance(media_clip,
	                                 AudioFileClip) else media_clip.audio
	final_clip = final_clip.set_audio(audio)
	final_clip.write_videofile(output_video_file, fps=24)

	# Clean up
	media_clip.close()
	final_clip.close()


def create_video_from_audio(audio_file,
                            output_video_file,
                            width=720,
                            height=480):
	"""
	Create a video with a black background and the audio from the input file.
	"""
	# Load the audio file
	audio_clip = AudioFileClip(audio_file)
	duration = audio_clip.duration

	# Create a background clip
	background_clip = ColorClip(size=(width, height),
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
