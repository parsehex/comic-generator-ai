import os
import json
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QComboBox, QTextEdit
from PyQt5.QtCore import Qt
from src.chunk_manager_gui import ChunkManagerGUI
from src.utils import chunkTextForTTS, create_audio, create_project_folder
from src.enums import ElevenLabsTTSModel, ElevenLabsTTSVoice
from dotenv import load_dotenv

load_dotenv()


class ScriptEditor(QWidget):

	def __init__(self, script_path=None, on_save_callback=None):
		super().__init__()
		self.script_path = script_path
		self.on_save_callback = on_save_callback
		self.init_ui()

	def init_ui(self):
		self.setWindowTitle('Script Editor')
		self.setGeometry(100, 100, 600, 400)

		layout = QVBoxLayout()

		self.text_edit = QTextEdit()
		layout.addWidget(self.text_edit)

		button_layout = QHBoxLayout()
		save_button = QPushButton('Save')
		save_button.clicked.connect(self.save_script)
		button_layout.addWidget(save_button)

		layout.addLayout(button_layout)

		self.setLayout(layout)

		if self.script_path and os.path.exists(self.script_path):
			with open(self.script_path, 'r') as f:
				self.text_edit.setText(f.read())

	def save_script(self):
		if not self.script_path:
			self.script_path, _ = QFileDialog.getSaveFileName(
			    self, 'Save Script', '', 'Text Files (*.txt)')

		if self.script_path:
			with open(self.script_path, 'w') as f:
				f.write(self.text_edit.toPlainText())
			self.close()

		if self.script_path and self.on_save_callback:
			self.on_save_callback(self.script_path)


class SetupWindow(QWidget):

	def __init__(self):
		super().__init__()
		self.init_ui()

	def init_ui(self):
		self.setWindowTitle('TTS Application Setup')
		self.setGeometry(100, 100, 400, 350)

		layout = QVBoxLayout()

		# Project folder selection
		folder_layout = QHBoxLayout()
		self.folder_label = QLabel('Use Existing Project Folder?')
		self.folder_button = QPushButton('Browse')
		self.folder_button.clicked.connect(self.select_folder)
		folder_layout.addWidget(self.folder_label)
		folder_layout.addWidget(self.folder_button)
		layout.addLayout(folder_layout)

		# Script selection
		script_layout = QHBoxLayout()
		self.script_label = QLabel('Select Script:')
		self.edit_script_button = QPushButton('New / Edit')
		self.edit_script_button.clicked.connect(self.edit_script)
		self.script_button = QPushButton('Browse')
		self.script_button.clicked.connect(self.select_script)
		script_layout.addWidget(self.script_label)
		script_layout.addWidget(self.edit_script_button)
		script_layout.addWidget(self.script_button)
		layout.addLayout(script_layout)

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

		# Buttons
		button_layout = QHBoxLayout()
		self.start_button = QPushButton('Start')
		self.start_button.clicked.connect(self.start_application)
		self.view_chunks_button = QPushButton('View Chunks')
		self.view_chunks_button.clicked.connect(self.view_chunks)
		button_layout.addWidget(self.start_button)
		button_layout.addWidget(self.view_chunks_button)
		layout.addLayout(button_layout)

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

	def update_script_path(self, new_path):
		self.script_path = new_path
		self.script_label.setText(f'Script: {os.path.basename(self.script_path)}')

	def edit_script(self):
		if self.script_path:
			self.script_editor = ScriptEditor(self.script_path,
			                                  self.update_script_path)
		else:
			self.script_editor = ScriptEditor(
			    on_save_callback=self.update_script_path)
		self.script_editor.show()

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

	def view_chunks(self):
		try:
			if not self.project_folder:
				self.project_folder = create_project_folder()
			has_chunks = os.path.exists(
			    os.path.join(self.project_folder, 'tts-chunks.json'))
			if not self.script_path and not has_chunks:
				self.script_label.setText('Please select a script first!')
				return

			if self.script_path:
				with open(self.script_path, 'r') as f:
					script_text = f.read()
				chunks = chunkTextForTTS(script_text)
			else:
				with open(os.path.join(self.project_folder, 'tts-chunks.json'),
				          'r') as f:
					chunks = json.load(f)

			print("Creating ChunkManagerGUI instance")
			ex = ChunkManagerGUI(chunks, self.project_folder)
			print("Showing ChunkManagerGUI")
			ex.show()
			ex.raise_()
			print("ChunkManagerGUI should be visible now")
		except Exception as e:
			print(f"An error occurred: {str(e)}")


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
