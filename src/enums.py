from enum import Enum


class ElevenLabsTTSModel(Enum):
	Turbo_v25 = 'eleven_turbo_v2_5'
	Turbo_v2 = 'eleven_turbo_v2'
	Multilingual_v2 = 'eleven_multilingual_v2'
	Monolingual_v1 = 'eleven_monolingual_v1'


class ElevenLabsTTSVoice(Enum):
	# not comprehensive of course
	# using descriptions from https://audio-generation-plugin.com/elevenlabs-premade-voices/
	#   this is a good resource of elevenlabs' premade voices

	Antoni = 'ErXwobaYiN019PkySvjV'
	Brian = 'nPczCjzI2devNBz1zQrb'  # deep, middle-aged male voice with an American accent


class TogetherAIFluxModel(Enum):
	Flux1SchnellFree = 'black-forest-labs/FLUX.1-schnell-Free'
	Flux1SchnellTurbo = 'black-forest-labs/FLUX.1-schnell'
	Flux1_1Pro = 'black-forest-labs/FLUX.1.1-pro'
	Flux1Pro = 'black-forest-labs/FLUX.1-pro'
