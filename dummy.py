from googletrans import Translator
with open('yt.txt') as f:
    file = f.read()
translator = Translator()

translated_text = translator.translate(file)
print(translated_text.text)

translated_text = translator.translate('안녕하세요.', dest='ja')
print(translated_text.text)

translated_text = translator.translate('veritas lux mea', src='la')
print(translated_text.text)