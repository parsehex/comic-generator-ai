import os
import json
import sys
from PyQt5.QtWidgets import QApplication
from src.chunk_manager_gui import ChunkManagerGUI
from src.utils import chunkTextForTTS, create_audio, create_project_folder
from src.enums import ElevenLabsTTSModel
from dotenv import load_dotenv

load_dotenv()


def save_chunks(chunks, project_folder):
	chunks_name = os.path.join(project_folder, 'tts-chunks.json')
	with open(chunks_name, 'w') as f:
		json.dump(chunks, f)


def process_script(script_text, script_location):
	if not script_text and not os.path.exists(script_location):
		raise SystemExit("Please provide a script or a valid script location")

	if not script_text and script_location:
		with open(script_location, 'r') as f:
			script_text = f.read()

	return script_text


def generate_audio(chunks, project_folder, tts_model):
	skipped = 0
	for i, chunk in enumerate(chunks):
		chunk_type = chunk['type']
		audio_name = f'{i}_{chunk_type}.mp3'
		chunk['audio'] = audio_name
		audio_exists = os.path.exists(os.path.join(project_folder, audio_name))

		if audio_exists:
			skipped += 1
			continue

		content = chunk['content']
		create_audio(content, audio_name, project_folder, tts_model)

	if skipped > 0:
		print(f"Skipped generating {skipped} audio files")


def run_gui(chunks, project_folder):
	app = QApplication(sys.argv)
	ex = ChunkManagerGUI(chunks, project_folder)
	ex.show()
	sys.exit(app.exec_())


def main():
	tts_model = ElevenLabsTTSModel.Turbo_v25.value
	script_text = ""
	script_location = "input-test.txt"

	script_text = process_script(script_text, script_location)
	chunks = chunkTextForTTS(script_text)
	project_folder = create_project_folder(reuse=True)

	chunks_name = os.path.join(project_folder, 'tts-chunks.json')
	if not os.path.exists(chunks_name):
		print(f"Saving text chunks to {chunks_name}")
		save_chunks(chunks, project_folder)
	else:
		with open(chunks_name, 'r') as f:
			existing_chunks = json.load(f)
		print('Comparing with existing text chunks')
		if existing_chunks != chunks:
			print('Chunks have changed, updating')
			save_chunks(chunks, project_folder)

	generate_audio(chunks, project_folder, tts_model)
	save_chunks(chunks, project_folder)

	run_gui(chunks, project_folder)


if __name__ == "__main__":
	main()
