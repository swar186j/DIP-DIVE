import random
import json

import torch

from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

# Prompt three most commonly asked FAQs
samples = "I'm sorry, but I cannot understand your query. 1.Dip-Dive is a web app with a goal of Sentiment analysis for depression detection. 2.Dip-Dive is your real time partner anytime and anywhere! 3.If you feel yourselves depressed or low, just diagnose yourselves immediatedly and consult the experts."

device = torch.device('cpu')

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "DiveBot"

def get_response(msg):
    sentence = tokenize(msg)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]
 
    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    if prob.item() > 0.85:      #Increasing specifisity to reduce incorrect classifications
        for intent in intents['intents']:
            if tag == intent["tag"]:
                return random.choice(intent['responses'])
    
    return f"Dear user, {samples} "


if __name__ == "__main__":
    print("Let's chat! (type 'quit' to exit)")
    while True:
        # sentence = "do you use credit cards?"
        sentence = input("You: ")
        if sentence == "quit":
            break

        resp = get_response(sentence)
        print(resp)

