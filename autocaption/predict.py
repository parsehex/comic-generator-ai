import json
import os
import shutil
import tempfile
from typing import List
from .autocaption import load_model, create_audio, transcribe_audio, add_subtitle
from whisper_timestamped.transcribe import TransformerWhisperAsOpenAIWhisper


class VideoCaptioner:

	model: TransformerWhisperAsOpenAIWhisper

	def __init__(self):
		"""Initialize the captioner"""
		m = load_model()
		self.model = m

	def add_captions(
	    self,
	    video_file_path: str,
	    transcript_file_path: str = '',
	    output_video: bool = True,
	    output_transcript: bool = True,
	    subs_position: str = "bottom75",
	    color: str = "white",
	    highlight_color: str = "yellow",
	    fontsize: float = 7.0,
	    max_chars: int = 20,
	    opacity: float = 0.0,
	    font: str = "Poppins/Poppins-ExtraBold.ttf",
	    stroke_color: str = "black",
	    stroke_width: float = 2.6,
	    kerning: float = -5.0,
	    right_to_left: bool = False,
	) -> List[str]:
		"""
        Add captions to a video file
        Returns a list of output file paths (video and/or transcript)
        """
		# Validate inputs
		if right_to_left and "Arial" not in font:
			raise ValueError("Right to left subtitles only work with Arial fonts")

		if subs_position not in [
		    "bottom75", "center", "top", "bottom", "left", "right"
		]:
			raise ValueError("Invalid subtitles position")

		# Create temporary directory for processing
		temp_dir = tempfile.mkdtemp()
		extension = os.path.splitext(video_file_path)[1]
		video_temp_path = os.path.join(temp_dir, f"input{extension}")
		shutil.copyfile(video_file_path, video_temp_path)

		# Get word-level information
		if transcript_file_path != '':
			with open(transcript_file_path) as f:
				wordlevel_info = json.loads(f.read())
		else:
			audiofilename = create_audio(video_temp_path)
			wordlevel_info = transcribe_audio(self.model, audiofilename)

		outputs = []

		# Generate output video with captions
		if output_video:
			outputfile = add_subtitle(
			    video_temp_path,
			    "other aspect ratio",  # v_type is unused
			    subs_position,
			    highlight_color,
			    fontsize,
			    opacity,
			    max_chars,
			    color,
			    wordlevel_info,
			    font,
			    stroke_color,
			    stroke_width,
			    kerning,
			    right_to_left,
			)
			outputs.append(outputfile)

		# Generate transcript file
		if output_transcript:
			transcript_file_output = os.path.join(temp_dir, "transcript_out.json")
			with open(transcript_file_output, "w") as f:
				f.write(json.dumps(wordlevel_info, indent=4))
			outputs.append(transcript_file_output)

		return outputs


# Example usage:
if __name__ == "__main__":
	captioner = VideoCaptioner()
	output_paths = captioner.add_captions(video_file_path="kingnobel.mp4",
	                                      kerning=5)
	print(f"Output files: {output_paths}")
