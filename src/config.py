import os
import yaml

config_path = os.path.realpath(
    os.path.join(os.path.dirname(__file__), '../config/config.yaml'))

with open(config_path, 'r') as file:
	config = yaml.safe_load(file)

DEFAULT_CHAT_MODEL = config['ai']['default_chat_model']
DEFAULT_IMAGE_MODEL = config['ai']['default_image_model']
DEFAULT_TTS_MODEL = config['ai']['default_tts_model']
DEFAULT_TTS_VOICE = config['ai']['default_tts_voice']
