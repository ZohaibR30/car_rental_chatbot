import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

import tflearn
import numpy as np
import tensorflow as tf
import random
import json 
import pickle

with open("intents.json") as file:
        data = json.load(file)
try:
    with open("data.pickle", "rb") as f:
        words, labels, training, output = pickle.load(f)


except:
    #LOADING AND PRE-PROCESSING JSON FILE  

    words = []
    labels = []
    docs_x = []
    docs_y = []

    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            wrds = nltk.word_tokenize(pattern)
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent["tag"])

        if intent["tag"] not in labels:
            labels.append(intent["tag"])

    words = [stemmer.stem(w.lower()) for w in words if w not in "?"]
    words = sorted(list(set(words)))

    labels = sorted(labels)

    #TRAINING AND TESTING
    #1) BAG OF WORDS IS USED THAT COUNTS OCCURENCE OF WORDS

    training = []
    output = []

    out_empty = [0 for _ in range(len(labels))]

    for x, doc in enumerate(docs_x):
        bag = []

        wrds = [stemmer.stem(w) for w in doc]

        for w in words:
            if w in wrds:
                bag.append(1)
            else:
                bag.append(0)

        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1

        training.append(bag)
        output.append(output_row)

    training = np.array(training)
    output = np.array(output)

    with open("data.pickle", "wb") as f:
        pickle.dump((words, labels, training, output), f)

    #MODEL

tf.reset_default_graph()

net = tflearn.input_data(shape=[None, len(training[0])])    #INPUT DATA (LENGTH OF INPUT DATA)
net = tflearn.fully_connected(net, 8)   #TWO HIDDEN LAYERS
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(output[0]), activation="softmax")    #OUTPUT LAYER
net = tflearn.regression(net)

#TRAIN

model = tflearn.DNN(net)    #TYPE OF NEURAL NETWORK

try:
    model.load("model.tflearn")
except:
    tf.reset_default_graph()

    net = tflearn.input_data(shape=[None, len(training[0])])    #INPUT DATA (LENGTH OF INPUT DATA)
    net = tflearn.fully_connected(net, 8)   #TWO HIDDEN LAYERS
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, len(output[0]), activation="softmax")    #OUTPUT LAYER
    net = tflearn.regression(net)

    #TRAIN

    model = tflearn.DNN(net)    #TYPE OF NEURAL NETWORK

    model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)
    model.save("model.tflearn")

def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]
    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1
    
    return np.array(bag)

def chat(msg):
    print("Start talking with the bot (type quit to stop)!")
    
    while True:
        inp = msg
        
        if inp.lower() == "quit":
            exit(0)
        
        results = model.predict([bag_of_words(inp, words)])
        results_index = np.argmax(results)
    
        tag = labels[results_index]
        for tg in data["intents"]:
            if tg['tag'] == tag:
                responses = tg['responses']
        
        return(random.choice(responses))

#chat()