import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QTextEdit


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
