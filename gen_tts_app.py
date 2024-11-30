import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QComboBox, QLabel, QFileDialog, QSpinBox, QLineEdit, QCheckBox
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
from src.clients import elevenlabs
from src.utils import saveB64Audio, chunk_text, get_text_from_url
from src.enums import ElevenLabsTTSModel, ElevenLabsTTSVoice
from src.format_tts import format_tts_text
import tempfile
import base64
from dotenv import load_dotenv

load_dotenv()


class TTSApp(QWidget):

	def __init__(self):
		super().__init__()
		self.initUI()
		self.player = QMediaPlayer()

	def initUI(self):
		layout = QVBoxLayout()

		# explanatory line: "Enter text or load from file/URL"
		layout.addWidget(QLabel("Enter text or load from file/URL:"))

		# File input
		file_layout = QHBoxLayout()
		self.file_input = QLineEdit()
		self.file_input.setPlaceholderText("Select a text file...")
		self.file_button = QPushButton("Browse")
		self.file_button.clicked.connect(self.load_file)
		file_layout.addWidget(self.file_input)
		file_layout.addWidget(self.file_button)
		layout.addLayout(file_layout)

		# URL input
		url_layout = QHBoxLayout()
		self.url_input = QLineEdit()
		self.url_input.setPlaceholderText("Enter URL...")
		self.url_button = QPushButton("Load URL")
		self.url_button.clicked.connect(self.load_url)
		url_layout.addWidget(self.url_input)
		url_layout.addWidget(self.url_button)
		layout.addLayout(url_layout)

		# Checkbox to reformat URL-extracted text
		self.reformat_checkbox = QCheckBox("Reformat URL-extracted text")
		layout.addWidget(self.reformat_checkbox)

		# Text input
		self.text_input = QTextEdit()
		layout.addWidget(QLabel("Input Text:"))
		layout.addWidget(self.text_input)

		# Voice selection
		self.voice_combo = QComboBox()
		self.voice_combo.addItems([voice.name for voice in ElevenLabsTTSVoice])
		layout.addWidget(QLabel("Select Voice:"))
		layout.addWidget(self.voice_combo)

		# Max chunk length
		self.chunk_length_spinbox = QSpinBox()
		self.chunk_length_spinbox.setRange(1, 5000)
		self.chunk_length_spinbox.setValue(5000)
		layout.addWidget(QLabel("Max Chunk Length:"))
		layout.addWidget(self.chunk_length_spinbox)

		# Buttons
		button_layout = QHBoxLayout()
		self.generate_button = QPushButton("Generate TTS")
		self.generate_button.clicked.connect(self.generate_tts)
		self.play_button = QPushButton("Play Audio")
		self.play_button.clicked.connect(self.play_audio)
		self.save_button = QPushButton("Save Audio")
		self.save_button.clicked.connect(self.save_audio)
		button_layout.addWidget(self.generate_button)
		button_layout.addWidget(self.play_button)
		button_layout.addWidget(self.save_button)
		layout.addLayout(button_layout)

		self.setLayout(layout)
		self.setWindowTitle('TTS Generator')
		self.show()

	def load_file(self):
		file_name, _ = QFileDialog.getOpenFileName(self, "Open Text File", "",
		                                           "Text Files (*.txt)")
		if file_name:
			with open(file_name, 'r') as file:
				self.text_input.setPlainText(file.read())

	def load_url(self):
		url = self.url_input.text()
		if url:
			text = get_text_from_url(url)
			if self.reformat_checkbox.isChecked():
				text = format_tts_text(text)
			self.text_input.setPlainText(text)

	def generate_tts(self):
		input_text = self.text_input.toPlainText()
		if not input_text:
			print("Please provide input text.")
			return

		char_count = len(input_text)
		tts_model = ElevenLabsTTSModel.Multilingual_v2.value
		tts_voice = ElevenLabsTTSVoice[self.voice_combo.currentText()].value
		max_chunk_length = self.chunk_length_spinbox.value()

		if char_count > max_chunk_length:
			chunks = chunk_text(input_text, max_chunk_length)
			print(
			    f'Text is too long ({char_count} characters), splitting into {len(chunks)} parts'
			)
			self.audio_chunks = [
			    elevenlabs.getSpeechB64(chunk, tts_model, tts_voice)
			    for chunk in chunks
			]
			print("TTS generated successfully for all chunks.")
		else:
			self.audio_chunks = [
			    elevenlabs.getSpeechB64(input_text, tts_model, tts_voice)
			]
			print("TTS generated successfully.")

	def play_audio(self):
		if not hasattr(self, 'audio_chunks'):
			print("Please generate TTS first.")
			return

		# Create a temporary file to store the audio
		with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
			temp_filename = temp_file.name
			for audio in self.audio_chunks:
				temp_file.write(base64.b64decode(audio))

		# Play the audio
		self.player.setMedia(QMediaContent(QUrl.fromLocalFile(temp_filename)))
		self.player.play()

	def save_audio(self):
		if not hasattr(self, 'audio_chunks'):
			print("Please generate TTS first.")
			return

		file_name, _ = QFileDialog.getSaveFileName(self, "Save Audio File",
		                                           "output/tts",
		                                           "MP3 Files (*.mp3)")
		if file_name:
			for i, audio in enumerate(self.audio_chunks):
				chunk_output_file = f"{os.path.splitext(file_name)[0]}_part{i+1}{os.path.splitext(file_name)[1]}"
				saveB64Audio(audio, chunk_output_file)
				print(f'Audio saved to {chunk_output_file}')


if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = TTSApp()
	sys.exit(app.exec_())
