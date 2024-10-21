import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QComboBox, QLabel, QFileDialog
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
from src.ai import elevenlabs
from src.utils import saveB64Audio
from src.enums import ElevenLabsTTSModel, ElevenLabsTTSVoice
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

		# Text input
		self.text_input = QTextEdit()
		layout.addWidget(QLabel("Input Text:"))
		layout.addWidget(self.text_input)

		# Voice selection
		self.voice_combo = QComboBox()
		self.voice_combo.addItems([voice.name for voice in ElevenLabsTTSVoice])
		layout.addWidget(QLabel("Select Voice:"))
		layout.addWidget(self.voice_combo)

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

	def generate_tts(self):
		input_text = self.text_input.toPlainText()
		if not input_text:
			print("Please provide input text.")
			return

		char_count = len(input_text)
		if char_count > 5000:
			print(
			    f'Input text is too long ({char_count} characters), max is 5000 characters'
			)
			return

		tts_model = ElevenLabsTTSModel.Multilingual_v2.value
		tts_voice = ElevenLabsTTSVoice[self.voice_combo.currentText()].value

		self.audio = elevenlabs.getSpeechB64(input_text, tts_model, tts_voice)
		print("TTS generated successfully.")

	def play_audio(self):
		if not hasattr(self, 'audio'):
			print("Please generate TTS first.")
			return

		# Create a temporary file to store the audio
		with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
			temp_filename = temp_file.name
			temp_file.write(base64.b64decode(self.audio))

		# Play the audio
		self.player.setMedia(QMediaContent(QUrl.fromLocalFile(temp_filename)))
		self.player.play()

	def save_audio(self):
		if not hasattr(self, 'audio'):
			print("Please generate TTS first.")
			return

		file_name, _ = QFileDialog.getSaveFileName(self, "Save Audio File", "",
		                                           "MP3 Files (*.mp3)")
		if file_name:
			saveB64Audio(self.audio, file_name)
			print(f'Audio saved to {file_name}')


if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = TTSApp()
	sys.exit(app.exec_())
