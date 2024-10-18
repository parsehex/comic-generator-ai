import sys
import json
import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QListWidget, QListWidgetItem
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
from playsound import playsound


class ChunkManagerGUI(QWidget):

	def __init__(self, chunks, project_folder):
		super().__init__()
		self.chunks = chunks
		self.project_folder = project_folder
		self.current_chunk = 0
		self.init_ui()

	def init_ui(self):
		self.setWindowTitle('Chunk Manager')
		self.setGeometry(100, 100, 600, 400)

		layout = QVBoxLayout()

		# Text edit for chunk content
		self.text_edit = QTextEdit()
		layout.addWidget(self.text_edit)

		# List widget for chunks
		self.chunk_list = QListWidget()
		layout.addWidget(self.chunk_list)

		# Buttons
		button_layout = QHBoxLayout()
		self.prev_button = QPushButton('Previous')
		self.next_button = QPushButton('Next')
		self.play_button = QPushButton('Play Audio')
		self.regenerate_button = QPushButton('Regenerate Audio')

		button_layout.addWidget(self.prev_button)
		button_layout.addWidget(self.next_button)
		button_layout.addWidget(self.play_button)
		button_layout.addWidget(self.regenerate_button)

		layout.addLayout(button_layout)

		# Status label
		self.status_label = QLabel()
		layout.addWidget(self.status_label)

		self.setLayout(layout)

		# Connect buttons to functions
		self.prev_button.clicked.connect(self.prev_chunk)
		self.next_button.clicked.connect(self.next_chunk)
		self.play_button.clicked.connect(self.play_audio)
		self.regenerate_button.clicked.connect(self.regenerate_audio)
		self.chunk_list.itemClicked.connect(self.jump_to_chunk)

		self.load_chunks()
		self.load_chunk()

	def load_chunks(self):
		self.chunk_list.clear()
		for i, chunk in enumerate(self.chunks):
			item = QListWidgetItem(f"Chunk {i + 1}: {chunk['type']}")
			self.chunk_list.addItem(item)

	def load_chunk(self):
		chunk = self.chunks[self.current_chunk]
		self.text_edit.setText(chunk['content'])
		self.status_label.setText(
		    f"Chunk {self.current_chunk + 1}/{len(self.chunks)} - Type: {chunk['type']}"
		)
		self.chunk_list.setCurrentRow(self.current_chunk)

	def prev_chunk(self):
		if self.current_chunk > 0:
			self.current_chunk -= 1
			self.load_chunk()

	def next_chunk(self):
		if self.current_chunk < len(self.chunks) - 1:
			self.current_chunk += 1
			self.load_chunk()

	def play_audio(self):
		i = self.current_chunk
		chunk = self.chunks[i]
		audio_path = chunk['audio']
		audio_path = os.path.join(self.project_folder, audio_path)

		if os.path.exists(audio_path):
			playsound(audio_path)
		else:
			self.status_label.setText("Audio file not found")

	def regenerate_audio(self):
		# Implement the logic to regenerate audio for the current chunk
		# You'll need to call your create_audio function here
		pass

	def jump_to_chunk(self, item):
		self.current_chunk = self.chunk_list.row(item)
		self.load_chunk()

	def closeEvent(self, event):
		# Save changes to chunks when closing the window
		with open(os.path.join(self.project_folder, 'tts-chunks.json'), 'w') as f:
			json.dump(self.chunks, f)
		event.accept()
