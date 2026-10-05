"""Optional CNN architecture. Train only with consented labelled handwriting datasets."""
def build_model():
 from tensorflow.keras import Sequential
 from tensorflow.keras.layers import Conv2D,MaxPooling2D,Dropout,Flatten,Dense
 return Sequential([Conv2D(32,3,activation='relu',input_shape=(128,128,1)),MaxPooling2D(),Conv2D(64,3,activation='relu'),MaxPooling2D(),Dropout(.25),Flatten(),Dense(64,activation='relu'),Dropout(.3),Dense(1,activation='sigmoid')])
