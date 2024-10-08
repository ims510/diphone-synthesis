import parselmouth
import textgrids
from parselmouth.praat import call
import spacy
from playsound import playsound
from typing import NamedTuple, List

def main():

	son = 'silai_final.wav'
	grille = 'silai_final.TextGrid'

	sound = parselmouth.Sound(son)
	segmentation = textgrids.TextGrid(grille)

	user_choices = get_user_input()

	phrase_ortho = " ".join(user_choices)
	
	display_sentence(user_choices) 

	phonemes = segmentation['labels']

	dico = dico_pron("dico_silai.txt")

	phrase_phonetique = generate_phrase_phonetique(phrase_ortho, dico)

	print(f"La transcription SAMPA de la phrase construite: {phrase_phonetique}")
	debut = synthese(phrase_phonetique, sound, phonemes)

	debut.save("resultat.wav", parselmouth.SoundFileFormat.WAV)
	playsound('resultat.wav')

def get_user_input():
    # Define the table as a list of lists
    table = [
        ["le chat noir grimpe", "le chien marron aboie", "le jeune garçon parle", "le chat beige saute", "la vieille femme glisse"],
        ["sur le toit", "sur le lit", "sur le sol"],
        ["en miaulant", "en sautant", "en riant", "en grattant", "en appuyant"],
        ["joyeusement", "bruyamment", "fortement", "les draps", "les rideaux"]
    ]

    # Get user input for each column
    choices = []
    for column in table:
        if len(choices) > 0:
            print(f"\nYour sentence so far: {' '.join(choices)}")
            print("-----------------------------------------------------------")

        print("\n".join(f"{i + 1}. {item}" for i, item in enumerate(column)))
        user_choice = input(f"Choose an element for your sentence (1-{len(column)}): ")
        print("-----------------------------------------------------------")
        # Validate user input
        while not user_choice.isdigit() or not (1 <= int(user_choice) <= len(column)):
            print("Invalid input. Please enter a valid number.")
            user_choice = input(f"Choose an element for your sentence (1-{len(column)}): ")

        # Append the chosen element to the choices list
        choices.append(column[int(user_choice) - 1])

    return choices


def display_sentence(user_choices):
	user_choices[0] = user_choices[0].capitalize()
	user_choices[len(user_choices)-1] =  user_choices[len(user_choices)-1] + "."
	print("\nLa phrase construite: ")
	print(" ".join(user_choices))


# on va créer le dictionnaire de prononciation
def dico_pron(dico_phon):
	dico = {}
	with open (dico_phon, 'r') as file:
		for line in file:
			key, value = line.strip().split('\t')
			dico[key] = value
	return dico

class PhoneticSymbol(NamedTuple):
	phonetic_symbol: str 
	pos: str = ""
	is_sentence_end: bool = False

def generate_phrase_phonetique(phrase_ortho, dico):
	spacy_model = spacy.load("fr_core_news_md")
	spacy_doc = spacy_model(phrase_ortho)
	phrase_phonetique: List[PhoneticSymbol] = []
	phrase_phonetique.append(PhoneticSymbol("_"))
	for i, token in enumerate(spacy_doc):
		mot_phonetique = dico[token.text]
		pos = token.pos_
		is_sentence_end = token.is_sent_end if token.is_sent_end is not None else False
		for symbol in mot_phonetique:
			phrase_phonetique.append(PhoneticSymbol(symbol, pos, is_sentence_end))
		# liaisons
		if token.text == "toit" and i < (len(spacy_doc) - 1) and spacy_doc[i+1].text == "en":
			phrase_phonetique.append(PhoneticSymbol("t"))
		elif token.text == "en" and i < (len(spacy_doc) - 1) and spacy_doc[i+1].text == "appuyant":
			phrase_phonetique.append(PhoneticSymbol("n"))

		
	phrase_phonetique.append(PhoneticSymbol("_", is_sentence_end=True))
	return phrase_phonetique

def synthese(phrase_phonetique: List[PhoneticSymbol], sound, phonemes):

	debut = sound.extract_part(0, 0.01, parselmouth.WindowShape.RECTANGULAR, 1, False)

	for i in range(len(phrase_phonetique) - 1):
		phoneme1 = phrase_phonetique[i]
		phoneme2 = phrase_phonetique[i + 1]
		# print(phoneme1, phoneme2)
		extrait = extraction_diphones(phoneme1.phonetic_symbol, phoneme2.phonetic_symbol, phonemes, sound)
		#extrait = modify_sound_pitch(extrait, pitch_factor=3)

		if phoneme1.pos == 'VERB' and phoneme2.pos == 'VERB':
			extrait = modify_sound_duration(extrait, duration_factor=0.9)
			extrait = modify_sound_pitch(extrait, pitch_factor=1)
		if phoneme1.is_sentence_end and phoneme2.is_sentence_end:
			extrait = modify_sound_duration(extrait, duration_factor=1.1)
			extrait = modify_sound_pitch(extrait, pitch_factor=0.9)

		extrait = modify_sound_duration(extrait, duration_factor=0.8)
		

		# if it's not a verb or end of sentence: extrait = modify_sound_duration(extrait, duration_factor=1)

		debut = debut.concatenate([debut, extrait])

	return debut


def extraction_diphones(phoneme1, phoneme2, diphones, sound):
	for a in range(len(diphones)-1):
		b = a + 1
		if diphones[a].text == phoneme1 and diphones[b].text == phoneme2:
			
			milieu_phoneme1 = diphones[a].xmin + (diphones[a].xmax - diphones[a].xmin) / 2
			milieu_phoneme1 = sound.get_nearest_zero_crossing(milieu_phoneme1, 1)

			milieu_phoneme2 = diphones[b].xmin + (diphones[b].xmax - diphones[b].xmin) / 2
			milieu_phoneme2 = sound.get_nearest_zero_crossing(milieu_phoneme2, 1)

			extrait = sound.extract_part(milieu_phoneme1, milieu_phoneme2, parselmouth.WindowShape.RECTANGULAR, 1, False)
			# print(phoneme1, phoneme2) #pour tester

			return extrait
	raise RuntimeError(f"diphone {phoneme1} {phoneme2} not found")

def modify_sound_duration(extrait, duration_factor):
	manipulation = call(extrait, "To Manipulation", 0.01, 75, 600) 
	duration_tier = call(manipulation, "Extract duration tier")
	call(duration_tier, "Remove points between", 0, extrait.duration)
	call(duration_tier, "Add point", extrait.duration/2, duration_factor)
	call([manipulation, duration_tier], "Replace duration tier")
	modified_sound = call(manipulation, "Get resynthesis (overlap-add)")
	return modified_sound

def modify_sound_pitch(extrait, pitch_factor):
	manipulation = call(extrait, "To Manipulation", 0.01, 75, 600)
	pitch_tier = call(manipulation, "Extract pitch tier")
	nb_values = call(pitch_tier, "Get number of points")
	if nb_values > 0:
		call(pitch_tier, "Multiply frequencies", extrait.xmin, extrait.xmax, pitch_factor)
		call([manipulation, pitch_tier], "Replace pitch tier")
		modified_sound = call(manipulation, "Get resynthesis (overlap-add)")
		return modified_sound
	else:
		return extrait



if __name__ == "__main__":
	main()

#TO DO:
	# make it work with capitals and full stop
	# user input with options?
		# add options to make it go fast, slow, high, low pitch 
	# generate plot like on praat 

	