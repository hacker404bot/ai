from flask import Flask, render_template, request
import pytesseract
from PIL import Image
import cv2
import numpy as np
import os
from gtts import gTTS
app = Flask(__name__)

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

braille = ['\u2834','\u2802','\u2806','\u2812','\u2832','\u2822','\u2816','\u2836','\u2826','\u2814',
           '\u2801','\u2803','\u2809','\u2819','\u2811','\u280b','\u281b','\u2813','\u280a','\u281a',
           '\u2805','\u2807','\u280d','\u281d','\u2815','\u280f','\u281f','\u2817','\u280e','\u281e',
           '\u2825','\u2827','\u283a','\u282d','\u283d','\u2835',
           '\u2831','\u2830','\u2823','\u283f','\u2800','\u282e','\u2810','\u283c','\u282b','\u2829',
           '\u282f','\u2804','\u2837','\u283e','\u2821','\u282c','\u2820','\u2824','\u2828','\u280c',
           '\u281c','\u2839','\u2808','\u282a','\u2833','\u283b','\u2818','\u2838']

English = ['0','1','2','3','4','5','6','7','8','9',
           'a','b','c','d','e','f','g','h','i','j',
           'k','l','m','n','o','p','q','r','s','t',
           'u','v','w','x','y','z',
           ':',';','<','=',' ','!','"','#','$','%',
           '&','','(',')','*','+',',','-','.','/',
           '>','?','@','[','\\',']','^','_']

def preprocess_image(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return gray

def extract_text_from_image(image_path):
    processed_image = preprocess_image(image_path)
    pil_image = Image.fromarray(processed_image)
    extracted_text = pytesseract.image_to_string(pil_image)
    return extracted_text.strip()

def Braille2English(BrailleText):
    return ''.join([English[braille.index(ch)] if ch in braille else '?' for ch in BrailleText])

def English2Braille(EnglishText):
    return ''.join([braille[English.index(ch)] if ch in English else '?' for ch in EnglishText])

# Convert text to speech and save as MP3
def text_to_speech(text, output_path):
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(output_path)
    return output_path



@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error="No file uploaded")
        
        file = request.files['file']
        
        if file.filename == '':
            return render_template('index.html', error="No file selected")
        
        if file:
            filename = 'uploaded_image.png'
            file_path = os.path.join('static', filename)
            file.save(file_path)
            
            try:
                extracted_text = extract_text_from_image(file_path)
                if extracted_text:
                    braille_text = English2Braille(extracted_text.lower())
                    english_from_braille = Braille2English(braille_text)
                    
                    # Generate audio file from extracted text
                    audio_filename = 'output_audio.mp3'
                    audio_path = os.path.join('static', audio_filename)
                    text_to_speech(extracted_text, audio_path)
                    
                    return render_template('index.html',
                                        extracted_text=extracted_text,
                                        braille_text=braille_text,
                                        english_from_braille=english_from_braille,
                                        image_path=filename,
                                       audio_path=audio_filename )
                else:
                    return render_template('index.html', error="No text detected in the image")
            except Exception as e:
                return render_template('index.html', error=f"Error: {str(e)}")
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)