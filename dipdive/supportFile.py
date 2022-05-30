#import necessary libraries
import cv2
import time
from keras.preprocessing import image
import numpy as np


c=0
flag=0
count = 0

#--------------------------------Sentiment Analysis Part-----------------------------------------
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')


#-----------------------------
#face expression recognizer initialization
from keras.models import model_from_json
model = model_from_json(open("facial_expression_model_structure.json", "r").read())
model.load_weights('facial_expression_model_weights.h5') #load weights


emotions = ('angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral')

def get_frame(num):
	global count

	camera_port=0

	timeout = time.time() + 40  
	

	# set the time out rule
	camera=cv2.VideoCapture(camera_port)
	#this makes a web cam object	
	# time.sleep(2)
	flag=1
	
	
	while time.time() < timeout:
		ret, img = camera.read()
		
		print(img.shape)
		
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		
		faces = face_cascade.detectMultiScale(gray, 1.3, 5)

		#print(faces) #locations of detected faces
		
		for (x,y,w,h) in faces:
			
			cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2) #draw rectangle to main image
			
			detected_face = img[int(y):int(y+h), int(x):int(x+w)] #crop detected face
			
			detected_face = cv2.cvtColor(detected_face, cv2.COLOR_BGR2GRAY) #transform to gray scale
			detected_face = cv2.resize(detected_face, (48, 48)) #resize to 48x48
			
			img_pixels = image.img_to_array(detected_face)
			img_pixels = np.expand_dims(img_pixels, axis = 0)
			
			img_pixels /= 255 #pixels are in scale of [0, 255]. normalize all pixels in scale of [0, 1]
			
			predictions = model.predict(img_pixels) #store probabilities of 7 expressions
			
			#find max indexed array 0: angry, 1:disgust, 2:fear, 3:happy, 4:sad, 5:surprise, 6:neutral
			max_index = np.argmax(predictions[0])
			
			emotion = emotions[max_index]

			if(emotion == 'sad' or emotion == 'fear'or emotion == 'angry' or emotion == 'disgust'):
				count = count+1
				print(count)
			
			if(count > 8):
				#write emotion text above rectangle
				count = 0
				#vid_dep=1
				cv2.putText(img, "Depression Detected", (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
				result="Depression Detected."
				
			else:
				cv2.putText(img, emotion + ":" + str(predictions[0][max_index]), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
				result = "No Depression Detected."
		imgencode=cv2.imencode('.jpg',img)[1]
		stringData=imgencode.tostring()
		yield (b'--frame\r\n'
			b'Content-Type: text/plain\r\n\r\n'+stringData+b'\r\n')
		
	
		
	camera.release()
		
	cv2.destroyAllWindow()
	

def get_score():
	if(count > 8):
		result="Depression Detected."
	else:
		result = "No Depression Detected."
	return result