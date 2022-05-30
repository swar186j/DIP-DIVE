#text
import utils
import nltk


#predict funtion
def predict(symptoms,username, num):
    punctuations = '''!()-[]{|};:'"\,<>./?@#$%^&*_~'''
    symptoms.lower()
    my_str= symptoms
    no_punct = ""
    for char in my_str:
        if char not in punctuations:
            no_punct = no_punct + char
    
    symptoms = no_punct
    utils.export("data/"+username+"-symptoms.txt", symptoms, "w")
    result = predictDepression(username, num)
    return result


def predictDepression(username, num):
    data = utils.getTrainData()
    #print(data)
    def get_words_in_text(text):	
        all_words = []
        for (words, sentiment) in text:
            all_words.extend(words)
        return all_words

    def get_word_features(wordlist):		
        wordlist = nltk.FreqDist(wordlist)
        #removes repeated words 
        word_features = wordlist.keys()
        return word_features

    		
    def extract_features(document):		
        document_words = set(document)
        #print(document_words)
        features = {}
        for word in word_features:
            features[word] = (word in document_words)
        #print(features)
        return features

    #allsetlength = len(data)
    #print(allsetlength)

    word_features = get_word_features(get_words_in_text(data))		
    training_set = nltk.classify.apply_features(extract_features, data)	
    test_set = data[88:]		
    classifier = nltk.NaiveBayesClassifier.train(training_set)			
    
    def classify(symptoms):
        return(classifier.classify(extract_features(symptoms.split())))      
        
    f = open("data/"+ username+"-symptoms.txt", "r")	
    f = [line for line in f if line.strip() != ""]	
    tot=0
    pos=0
    neg=0
    
    for symptom in f:
        tot = tot + 1
        print("syms:" ,symptom)
        result = classify(symptom)
        
        print("res:",result)
        if(result == "Depression Detected"):
            neg = neg + 1
        elif(result == "No Depresion"):
            pos=pos+1

    pos = tot - neg
    dep_score=(neg/tot)*100
    dep_score= '{0:.2f}'.format(dep_score)
    if(dep_score != 0):
        result = "Depression Detected:" + str(dep_score) + "%"
        
    else:
        result = "No Depression Detected."
    return result

























'''
def speech_text():	
	
	# Exception handling to handle
	# exceptions at the runtime
	try:
		
		# use the microphone as source for input.
		with sr.Microphone() as source2:
			
			# wait for a second to let the recognizer
			# adjust the energy threshold based on
			# the surrounding noise level
			r.adjust_for_ambient_noise(source2, duration=0.2)
			
			#listens for the user's input
			audio2 = r.listen(source2)
			
			# Using ggogle to recognize audio
			MyText = r.recognize_google(audio2)
			MyText = MyText.lower()

			
			return(MyText)
			
	except sr.RequestError as e:
		return("Could not request results; {0}".format(e))
		
	except sr.UnknownValueError:
		return("unknown error occured")
    '''