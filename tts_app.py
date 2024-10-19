import os
import json
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QComboBox
from PyQt5.QtCore import Qt
from src.chunk_manager_gui import ChunkManagerGUI
from src.utils import chunkTextForTTS, create_audio, create_project_folder
from src.enums import ElevenLabsTTSModel, ElevenLabsTTSVoice
from dotenv import load_dotenv

load_dotenv()


class SetupWindow(QWidget):

	def __init__(self):
		super().__init__()
		self.init_ui()

	def init_ui(self):
		self.setWindowTitle('TTS Application Setup')
		self.setGeometry(100, 100, 400, 300)

		layout = QVBoxLayout()

		# Script selection
		script_layout = QHBoxLayout()
		self.script_label = QLabel('Select Script:')
		self.script_button = QPushButton('Browse')
		self.script_button.clicked.connect(self.select_script)
		script_layout.addWidget(self.script_label)
		script_layout.addWidget(self.script_button)
		layout.addLayout(script_layout)

		# Project folder selection
		folder_layout = QHBoxLayout()
		self.folder_label = QLabel('Select Project Folder:')
		self.folder_button = QPushButton('Browse')
		self.folder_button.clicked.connect(self.select_folder)
		folder_layout.addWidget(self.folder_label)
		folder_layout.addWidget(self.folder_button)
		layout.addLayout(folder_layout)

		# TTS Model selection
		model_layout = QHBoxLayout()
		self.model_label = QLabel('Select TTS Model:')
		self.model_combo = QComboBox()
		for model in ElevenLabsTTSModel:
			self.model_combo.addItem(model.name, model.value)
		model_layout.addWidget(self.model_label)
		model_layout.addWidget(self.model_combo)
		layout.addLayout(model_layout)

		# Voice selection
		voice_layout = QHBoxLayout()
		self.voice_label = QLabel('Select Voice:')
		self.voice_combo = QComboBox()
		for voice in ElevenLabsTTSVoice:
			self.voice_combo.addItem(voice.name, voice.value)
		voice_layout.addWidget(self.voice_label)
		voice_layout.addWidget(self.voice_combo)
		layout.addLayout(voice_layout)

		# Start button
		self.start_button = QPushButton('Start')
		self.start_button.clicked.connect(self.start_application)
		layout.addWidget(self.start_button, alignment=Qt.AlignmentFlag.AlignCenter)

		self.setLayout(layout)

		self.script_path = None
		self.project_folder = None

	def select_script(self):
		file_dialog = QFileDialog()
		self.script_path, _ = file_dialog.getOpenFileName(self, 'Select Script',
		                                                  '', 'Text Files (*.txt)')
		if self.script_path:
			self.script_label.setText(
			    f'Script: {os.path.basename(self.script_path)}')

	def select_folder(self):
		folder_dialog = QFileDialog()
		self.project_folder = folder_dialog.getExistingDirectory(
		    self, 'Select Project Folder')
		if self.project_folder:
			self.folder_label.setText(
			    f'Project Folder: {os.path.basename(self.project_folder)}')

	def start_application(self):
		if not self.script_path:
			self.script_label.setText('Please select a script first!')
			return
		if not self.project_folder:
			self.project_folder = create_project_folder()

		tts_model = self.model_combo.currentData()
		voice_id = self.voice_combo.currentData()
		self.hide()
		self.app = TTSApplication(self.script_path, self.project_folder, tts_model,
		                          voice_id)
		self.app.run()
		self.close()


# TODO allow creating new script from GUI
#   opens a new window with text editor


class TTSApplication:

	def __init__(self, script_path, project_folder, tts_model, voice_id):
		self.script_path = script_path
		self.project_folder = project_folder
		self.tts_model = tts_model
		self.voice_id = voice_id
		self.script_text = ""
		self.chunks = []

	def process_script(self):
		with open(self.script_path, 'r') as f:
			self.script_text = f.read()

	def save_chunks(self):
		chunks_name = os.path.join(self.project_folder, 'tts-chunks.json')
		with open(chunks_name, 'w') as f:
			json.dump(self.chunks, f)

	def generate_audio(self):
		skipped = 0
		for i, chunk in enumerate(self.chunks):
			chunk_type = chunk['type']
			audio_name = f'{i}_{chunk_type}.mp3'
			chunk['audio'] = audio_name
			audio_exists = os.path.exists(
			    os.path.join(self.project_folder, audio_name))

			if audio_exists:
				skipped += 1
				continue

			content = chunk['content']
			create_audio(content, audio_name, self.project_folder, self.tts_model,
			             self.voice_id)

		if skipped > 0:
			print(f"Skipped generating {skipped} audio files")

	def run_gui(self):
		app = QApplication.instance()
		if app is None:
			app = QApplication(sys.argv)
		ex = ChunkManagerGUI(self.chunks, self.project_folder)
		ex.show()
		sys.exit(app.exec_())

	def run(self):
		self.process_script()
		self.chunks = chunkTextForTTS(self.script_text)

		chunks_name = os.path.join(self.project_folder, 'tts-chunks.json')
		if not os.path.exists(chunks_name):
			print(f"Saving text chunks to {chunks_name}")
			self.save_chunks()
		else:
			with open(chunks_name, 'r') as f:
				existing_chunks = json.load(f)
			print('Comparing with existing text chunks')
			if existing_chunks != self.chunks:
				print('Chunks have changed, updating')
				self.save_chunks()

		self.generate_audio()
		self.save_chunks()
		self.run_gui()


def main():
	app = QApplication(sys.argv)
	setup_window = SetupWindow()
	setup_window.show()
	sys.exit(app.exec_())


if __name__ == "__main__":
	main()
