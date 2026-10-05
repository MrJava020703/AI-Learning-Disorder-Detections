import joblib
from sklearn.metrics import classification_report,roc_auc_score,confusion_matrix
def evaluate(model_path,X_test,y_test):
 model=joblib.load(model_path)['model']; pred=model.predict(X_test);prob=model.predict_proba(X_test)[:,1]
 print(classification_report(y_test,pred));print('ROC-AUC:',roc_auc_score(y_test,prob));print(confusion_matrix(y_test,pred))
