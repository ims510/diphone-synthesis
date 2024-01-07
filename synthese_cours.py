import matplotlib.pyplot as plt
import parselmouth
import textgrids
#librarie à importer pour faire les prosodies:
from parselmouth.praat import call #on peut faire parselmout.praat.call si on ne veut pas importer ça


def main():

    son = 'silai.wav'
    grille = 'silai.TextGrid'

    sound = parselmouth.Sound(son)
    segmentation = textgrids.TextGrid(grille)

    phonemes = segmentation['phonemes']
    phrase_ortho = 'sur le toit'

    dico = dico_pron("dico_UTF8.txt")

    debut = synthese(phrase_ortho, dico, sound, phonemes)

    debut.save("resultat.wav", parselmouth.SoundFileFormat.WAV)

#on va créer le dictionnaire de prononciation
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
        phrase_phonetique.append(dico[mot])  #if we want to do synthese word by word it's here that will have to change
        
    phrase_phonetique = "".join(phrase_phonetique) #you can add _ to add pauses
    print(phrase_phonetique) #juste pour tester, à supprimer après
    debut = sound.extract_part(0, 0.01, parselmouth.WindowShape.RECTANGULAR, 1, False) #create a bit of sound file 
    for i in range(len(phrase_phonetique)-1):
        diphone = phrase_phonetique[i] + phrase_phonetique[i+1]
        phoneme1 = diphone[0]
        phoneme2 = diphone[1]
        extrait = extraction_diphones(phoneme1, phoneme2, phonemes, sound)
        print(type(debut), type(extrait)) #pour tester pq il y a des mots ou il trouve pas les sons
        
        debut = debut.concatenate([debut,extrait]) #can use a list as an argument for the function concatenate
    return debut

for phoneme in range(len(phrase_phonetique)-1): # or another way of doing: for position, phoneme in enumerate(phrase_phonetique[0:len(phrase_phonetique-1)])
    phoneme1=phrase_phonetique[phoneme]
    phoneme2=phrase_phonetique[phoneme+1]    
    for a in range(len(diphones)): #going through the textgrid, could have done for index, phoneme in diphones 
        b = a + 1
        if diphones[a].text == phoneme1 and diphones[b].text == phoneme2:
            
            milieu_phoneme1 = diphones[a].xmin + (diphones[a].xmax - diphones[a].xmin) / 2
            milieu_phoneme1 = sound.get_nearest_zero_crossing(milieu_phoneme1, 1)

            milieu_phoneme2 = diphones[b].xmin + (diphones[b].xmax - diphones[b].xmin) / 2
            milieu_phoneme2 = sound.get_nearest_zero_crossing(milieu_phoneme2, 1)

            extrait = sound.extract_part(milieu_phoneme1, milieu_phoneme2, parselmouth.WindowShape.RECTANGULAR,1,False) #c'est le diphone
            #you can make a function here that takes extrait as argument, and changes it to call blah blah
            allongement = 2 #ca va doubler la duree (un facteur mis artificiellement pour que ca marche, pour etre sur a l'ecoute que la phrase est bien allongee - NOUS DEVONS DETERMINER CE CHIFFRE, Il faut determiner une ou deux position dans la prhase (avant le verbe et avant la fin de la phrase_ on peut l'allonger de 2 mais le reste de temps c'est d'allonger moins. Soit on trouve le verbe dans une liste et on dit si verbe, allonge. Mieux si on utilise une libraire pour trouver le POS. 
            #on peut aussi arranger le script pour avoir des fonctions, des choix. On pourrait que la phrase soit prononcee vite ou doucement))
            
            ################################################PROSODIE(MODIF DUREE)#################
            #in praat: manip = To Manipulation: 0.01, 75, 600
            manipulation = call(extrait, "To Manipulation", 0.01, 75, 600) #to move after extraction
            duration_tier = call(manipulation, "Extract duration tier")
            call(duration_tier, "Remove points between", 0, extrait.duration)
            call(duration_tier, "Add point", extrait.duration/2,allongement)
            call([manipulation,duration_tier], "Replace duration tier")
            extrait = call(manipulation, "Get resynthesis (overlap-add)")


            debut = debut.concatenate([debut,extrait])



if __name__ == "__main__":
    main()


# #to show a plot of the sound:
# #plt.figure()
# #plt.plot(sound.xs(),sound.values.T)
# #plt.xlabel('time')
# #plt.ylabel('amplitude')
# #plt.show()

# this allows you to get the content of the first box: diphones[0].text
# this allows you to get the beginning and end time of the diphone: diphones[0].xmin and diphones[0].xmax

# on peut faire aussi: 
# from parselmouth.praat import call 
# parselmouth.praat.call(arg1, commande, ...)