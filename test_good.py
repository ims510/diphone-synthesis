import parselmouth
import textgrids
from parselmouth.praat import call

def main():

    son = 'silai_final.wav'
    grille = 'silai_final.TextGrid'

    sound = parselmouth.Sound(son)
    segmentation = textgrids.TextGrid(grille)

    phonemes = segmentation['labels']
    phrase_ortho = 'la vieille femme glisse sur le sol'

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
    phrase_phonetique=[] 

    for mot in phrase_ortho.split(" "):
        phrase_phonetique.append(dico[mot])
        
    phrase_phonetique = "".join(phrase_phonetique)
    print(phrase_phonetique) #juste pour tester, à supprimer après
    debut = sound.extract_part(0, 0.01, parselmouth.WindowShape.RECTANGULAR, 1, False)
    for i in range(len(phrase_phonetique)-1):
        diphone = phrase_phonetique[i] + phrase_phonetique[i+1]
        phoneme1 = diphone[0]
        phoneme2 = diphone[1]
        extrait = extraction_diphones(phoneme1, phoneme2, phonemes, sound)
        print(type(debut), type(extrait)) #pour tester pq il y a des mots ou il trouve pas les sons
        
        debut = debut.concatenate([debut,extrait])
    return debut

def extraction_diphones(phoneme1, phoneme2, diphones, sound):
    for a in range(len(diphones)):
        b = a + 1
        if diphones[a].text == phoneme1 and diphones[b].text == phoneme2:
            
            milieu_phoneme1 = diphones[a].xmin + (diphones[a].xmax - diphones[a].xmin) / 2
            milieu_phoneme1 = sound.get_nearest_zero_crossing(milieu_phoneme1, 1)

            milieu_phoneme2 = diphones[b].xmin + (diphones[b].xmax - diphones[b].xmin) / 2
            milieu_phoneme2 = sound.get_nearest_zero_crossing(milieu_phoneme2, 1)

            extrait = sound.extract_part(milieu_phoneme1, milieu_phoneme2, parselmouth.WindowShape.RECTANGULAR, 1, False)
            print(phoneme1, phoneme2) #pour tester

            # Modify the duration of the extracted sound
            extrait = modify_sound_duration(extrait)

            return extrait

def modify_sound_duration(sound):
    allongement = 2 
    manipulation = call(sound, "To Manipulation", 0.01, 75, 600)  # to move after extraction
    duration_tier = call(manipulation, "Extract duration tier")
    call(duration_tier, "Remove points between", 0, sound.duration)
    call(duration_tier, "Add point", sound.duration/2, allongement)
    call([manipulation, duration_tier], "Replace duration tier")
    modified_sound = call(manipulation, "Get resynthesis (overlap-add)")
    return modified_sound

if __name__ == "__main__":
    main()
