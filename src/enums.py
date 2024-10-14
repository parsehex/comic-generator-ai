from enum import Enum


class ElevenLabsTTSModel(Enum):
	Turbo_v25 = 'eleven_turbo_v2_5'
	Turbo_v2 = 'eleven_turbo_v2'
	Multilingual_v2 = 'eleven_multilingual_v2'
	Monolingual_v1 = 'eleven_monolingual_v1'


class TogetherAIFluxModel(Enum):
	Flux1SchnellFree = 'black-forest-labs/FLUX.1-schnell-Free'
	Flux1SchnellTurbo = 'black-forest-labs/FLUX.1-schnell'
	Flux1_1Pro = 'black-forest-labs/FLUX.1.1-pro'
	Flux1Pro = 'black-forest-labs/FLUX.1-pro'
