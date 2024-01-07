import spacy

sentence = "Le chien marron aboie sur le toit en sautant joyeusement"
spacy_model = spacy.load("fr_core_news_md")
spacy_doc = spacy_model(sentence)
for token in spacy_doc:
    print(token)
    if token.is_sent_end:
        print(f"{token} -> sfarsit de propositie")