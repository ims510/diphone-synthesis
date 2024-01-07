import parselmouth
import textgrids
from parselmouth.praat import call
import spacy

def main():

    son = 'projet/silai_final.wav'
    grille = 'projet/silai_final.TextGrid'

    sound = parselmouth.Sound(son)
    segmentation = textgrids.TextGrid(grille)

    phonemes = segmentation['labels']
    phrase_ortho = 'la femme glisse sur le sol'

    dico = dico_pron("dico_silai.txt")

    debut = synthese(phrase_ortho, dico, sound, phonemes)

    debut.save("resultat.wav", parselmouth.SoundFileFormat.WAV)

# on va créer le dictionnaire de prononciation
def dico_pron(dico_phon):
    dico = {}
    with open (dico_phon, 'r') as file:
        for line in file:
            key, value = line.strip().split('\t')
            dico[key] = value
    return dico

def synthese(phrase_ortho, dico, sound, phonemes):
    spacy_model = spacy.load("fr_core_news_md")
    spacy_doc = spacy_model(phrase_ortho)

    debut = sound.extract_part(0, 0.01, parselmouth.WindowShape.RECTANGULAR, 1, False)

    for token in spacy_doc:
        mots_phonetiques = []  # Initialize the list for each token
        mots_phonetiques.append(dico[token.text])
        phrase_phonetique = "".join(mots_phonetiques)
        print(phrase_phonetique)  # just for testing, remove later
        print(token.pos_)

        for i in range(len(phrase_phonetique) - 1):
            diphone = phrase_phonetique[i] + phrase_phonetique[i + 1]
            phoneme1 = diphone[0]
            phoneme2 = diphone[1]
            extrait = extraction_diphones(phoneme1, phoneme2, phonemes, sound)
            #extrait = modify_sound_pitch(extrait, pitch_factor=3)

            if token.pos_ == 'VERB':
                print("#########found verb#########")
                extrait = modify_sound_duration(extrait, duration_factor=1.2)
                extrait = modify_sound_pitch(extrait, pitch_factor=1)
            elif token.is_sent_end:
                extrait = modify_sound_duration(extrait, duration_factor=1.4)
                extrait = modify_sound_pitch(extrait, pitch_factor=1)
            else:
                extrait = modify_sound_duration(extrait, duration_factor=1)

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
            print(phoneme1, phoneme2) #pour tester



            return extrait

def modify_sound_duration(extrait, duration_factor):
    manipulation = call(extrait, "To Manipulation", 0.01, 75, 600)  # to move after extraction
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



if __name__ == "__main__":
    main()

#TO DO:
    # pronunciation link between "le toit __ en miaulant" and "le sol en____appuyant"
    # make it work with capitals and full stop
    # user input with options?
		# add options to make it go fast, slow, high, low pitch 
    # generate plot like on praat 
    