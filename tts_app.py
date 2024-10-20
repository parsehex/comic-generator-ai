import sys
from PyQt5.QtWidgets import QApplication
from src.gui.windows.setup_window import SetupWindow
from dotenv import load_dotenv

load_dotenv()


def main():
	app = QApplication(sys.argv)
	setup_window = SetupWindow()
	setup_window.show()
	sys.exit(app.exec_())


if __name__ == "__main__":
	main()
