import parselmouth
import textgrids
import os
import logging
import spacy

def load_audio(file_path):
    try:
        return parselmouth.Sound(file_path)
    except Exception as e:
        logging.error(f"Error loading audio file {file_path}: {str(e)}")
        return None

def load_textgrid(file_path):
    try:
        return textgrids.TextGrid(file_path)
    except Exception as e:
        logging.error(f"Error loading TextGrid file {file_path}: {str(e)}")
        return None

def load_spacy_model():
    try:
        return spacy.load("fr_core_news_sm")
    except Exception as e:
        logging.error(f"Error loading Spacy French model: {str(e)}")
        return None

def main():
    audio_file = 'silai.wav'
    textgrid_file = 'silai.TextGrid'
    output_file = 'resultat.wav'
    phrase_ortho = 'le chien marron'
    pronunciation_dict_file = 'dico_UTF8.txt'

    sound = load_audio(audio_file)
    if sound is None:
        return

    segmentation = load_textgrid(textgrid_file)
    if segmentation is None:
        return

    dico = load_pronunciation_dict(pronunciation_dict_file)
    if dico is None:
        return

    spacy_model = load_spacy_model()
    if spacy_model is None:
        return

    synthesis(sound, segmentation['phonemes'], phrase_ortho, dico, output_file, spacy_model)

def load_pronunciation_dict(file_path):
    try:
        dico = {}
        with open(file_path, 'r') as file:
            for line in file:
                key, value = line.strip().split('\t')
                dico[key] = value
        return dico
    except Exception as e:
        logging.error(f"Error loading pronunciation dictionary {file_path}: {str(e)}")
        return None

def synthesis(sound, phonemes, phrase_ortho, dico, output_file, spacy_model):
    phrase_phonetique = [dico[mot] for mot in phrase_ortho.split(" ")]

    try:
        debut = sound.extract_part(0, 0.01, parselmouth.WindowShape.RECTANGULAR, 1, False)
    except Exception as e:
        logging.error(f"Error extracting initial part of audio: {str(e)}")
        return

    spacy_doc = spacy_model(phrase_ortho)

    for i, token in enumerate(spacy_doc):
        is_verb = token.pos_ == 'VERB'
        is_end_of_sentence = token.is_sent_end or (i == len(spacy_doc) - 1)

        diphone = phrase_phonetique[i] if i < len(phrase_phonetique) else ""  # Handle phrases shorter than expected
        extrait = extraction_diphones(diphone, phonemes, sound)

        if extrait is not None:
            try:
                # Extend duration before a verb
                if is_verb:
                    extrait = modify_duration(extrait, duration_factor=1.5)  # Example: extend duration by 50%

                # Extend duration before the end of a sentence
                if is_end_of_sentence:
                    extrait = modify_duration(extrait, duration_factor=1.3)  # Example: extend duration by 30%

                # Apply pitch modification if needed
                extrait = modify_pitch(extrait, pitch_factor=1.2)  # Example: increase pitch by 20%
                
                # Concatenate the modified diphone to the synthesized output
                debut = debut.concatenate([debut, extrait])
            except Exception as e:
                logging.error(f"Error processing diphone '{diphone}': {str(e)}")

    try:
        # Apply prosody modeling if needed
        debut = modify_prosody(debut)
        
        # Save the synthesized and modified audio
        debut.save(output_file, parselmouth.SoundFileFormat.WAV)
    except Exception as e:
        logging.error(f"Error saving synthesized audio: {str(e)}")

def extraction_diphones(diphone, phonemes, sound):
    for a in range(len(phonemes) - 1):
        b = a + 1
        if phonemes[a].text == diphone[0] and phonemes[b].text == diphone[1]:
            try:
                milieu_phoneme1 = phonemes[a].xmin + (phonemes[a].xmax - phonemes[a].xmin) / 2
                milieu_phoneme1 = sound.get_nearest_zero_crossing(milieu_phoneme1, 1)

                milieu_phoneme2 = phonemes[b].xmin + (phonemes[b].xmax - phonemes[b].xmin) / 2
                milieu_phoneme2 = sound.get_nearest_zero_crossing(milieu_phoneme2, 1)

                extrait = sound.extract_part(milieu_phoneme1, milieu_phoneme2, parselmouth.WindowShape.RECTANGULAR, 1, False)
                return extrait
            except Exception as e:
                logging.error(f"Error extracting diphone '{diphone}': {str(e)}")
                return None

def modify_pitch(audio_segment, pitch_factor):
    return audio_segment.pitch_shift(pitch_factor)

def modify_duration(audio_segment, duration_factor):
    return audio_segment.speedup(playback_speed=duration_factor)

def modify_prosody(audio_segment):
    # Implement prosody modeling if needed
    # This can include changes in intonation, stress, etc.
    return audio_segment  # Placeholder, modify as needed

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()