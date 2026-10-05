"""Train baseline Random Forest screening models away from the live API."""
from pathlib import Path
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from preprocess import load_dataset, FEATURES
def train(csv_path='../datasets/screening.csv', output='../models'):
    df=load_dataset(csv_path); Path(output).mkdir(exist_ok=True); X=df[FEATURES]
    for target,name in [('dyslexia_label','dyslexia_model.pkl'),('dysgraphia_label','dysgraphia_model.pkl')]:
        xtr,xte,ytr,yte=train_test_split(X,df[target],test_size=.2,stratify=df[target],random_state=42)
        model=RandomForestClassifier(n_estimators=300,class_weight='balanced',random_state=42).fit(xtr,ytr)
        print(target,'validation accuracy',model.score(xte,yte)); joblib.dump({'model':model,'features':FEATURES},Path(output)/name)
if __name__=='__main__': train()
