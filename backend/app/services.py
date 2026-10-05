import re
from collections import Counter
from PIL import Image, ImageOps, ImageEnhance
from .core import settings
COMMON={'the','and','a','to','of','in','is','it','for','on','with','this','that','i','my','was','we','he','she','they','at','as','are','be','have','has','had','from','or'}
def analyze_text(text):
    words=re.findall(r"[A-Za-z']+",text.lower()); sentences=[s for s in re.split(r'[.!?]+',text) if s.strip()]; counts=Counter(words)
    unusual=[w for w in words if len(w)>2 and w not in COMMON and (len(w)>14 or re.search(r'(.)\1\1',w))]
    return {'word_count':len(words),'character_count':len(text),'sentence_count':len(sentences),'average_word_length':round(sum(map(len,words))/max(1,len(words)),2),'vocabulary_diversity':round(len(set(words))/max(1,len(words)),2),'repeated_word_count':sum(v-1 for v in counts.values() if v>1),'possible_spelling_patterns':len(unusual),'language_hint':'Hindi/English-ready design'}
def risk_level(score): return 'High' if score>=70 else 'Moderate' if score>=40 else 'Low'
def predict(questionnaire,reading,writing,nlp):
    q=lambda key:float(questionnaire.get(key,0) or 0)
    read=sum(q(x) for x in ['reading_difficulty','letter_confusion','spelling_difficulty','comprehension_difficulty'])/20
    write=sum(q(x) for x in ['spacing_irregularity','letter_formation','writing_fatigue','alignment_difficulty'])/20
    lang=min(1,(nlp['possible_spelling_patterns']+nlp['repeated_word_count'])/10)
    dyslexia=round(min(96,18+58*read+20*lang),1); dysgraphia=round(min(96,16+62*write+16*lang),1); overall=round(dyslexia*.52+dysgraphia*.48,1)
    indicators=[]
    if q('spelling_difficulty')>=3: indicators.append('Higher spelling-error frequency in reported responses')
    if q('spacing_irregularity')>=3: indicators.append('Irregular word spacing reported')
    if q('letter_confusion')>=3: indicators.append('Letter-recognition and reversal indicators')
    if nlp['repeated_word_count']>2: indicators.append('Repeated-word pattern detected in writing sample')
    if not indicators: indicators=['No strong single indicator; use results alongside educator observation']
    return {'dyslexia_score':dyslexia,'dysgraphia_score':dysgraphia,'overall_risk':overall,'risk_level':risk_level(overall),'confidence':round(min(.93,.62+.03*len(questionnaire)),2),'indicators':indicators}
def ocr_image(path):
    try:
        import pytesseract
        if settings.tesseract_cmd: pytesseract.pytesseract.tesseract_cmd=settings.tesseract_cmd
        image=ImageEnhance.Contrast(ImageOps.autocontrast(Image.open(path).convert('L'))).enhance(1.6)
        return pytesseract.image_to_string(image,config='--psm 6').strip()
    except Exception as exc: raise RuntimeError('OCR could not run. Install Tesseract and set TESSERACT_CMD. '+str(exc))
