"""Feature preparation for ethically sourced, consented screening research data."""
import pandas as pd
FEATURES=['reading_difficulty','letter_confusion','spelling_difficulty','comprehension_difficulty','spacing_irregularity','letter_formation','writing_fatigue','alignment_difficulty']
def load_dataset(path):
    df=pd.read_csv(path)
    missing=set(FEATURES+['dyslexia_label','dysgraphia_label'])-set(df.columns)
    if missing: raise ValueError(f'Missing required columns: {missing}')
    return df[FEATURES+['dyslexia_label','dysgraphia_label']].dropna()
