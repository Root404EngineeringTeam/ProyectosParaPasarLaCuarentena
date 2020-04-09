import re
import yaml
import string
import random
import unidecode
import Levenshtein

class Conversation():

    def __init__(self):
        self.dictionary = []
        self.context = {}

    def get_context(self,channel):
        key = "%s" %(channel.id)
        if key in self.context.keys():
            return self.context[key]

        else:
            return ''

    def set_context(self, channel, value):
        key = "%s" %(channel.id)
        self.context[key] = value

    def clear_context(self, channel):
        key = "%s" %(channel.id)
        self.context[key] = ''

    def set_context_var(self, channel, var, val):
        key = "%s.%s" %(channel.id, var)
        self.context[key] = val

    def get_context_var(self, channel, var):
        key = "%s.%s" %(channel.id, var)
        if key in self.context.keys():
            return self.context[key]

        else:
            return ''

    def load_dictionary(self, file):
        file = open(file)
        content = file.read()
        file.close()

        loaded = yaml.load(content)

        for question, answer in loaded:
            if isinstance(question, list):
                for sub_question in question:
                    self.dictionary.append([self.clear_string(sub_question), answer])
            else:
                self.dictionary.append([self.clear_string(question), answer])

    def clear_string(self, text):
        text = text.lower()
        text = unidecode.unidecode(text)
        text = re.sub(r'\"(.+)\"', "", text)
        text = re.sub(r'([0-9]+)', "", text)
        text = re.sub(r'(^e+r+i+\s+)|(\s+e+r+i+$)|(\s+e+r+i+\s+)', "", text)
        text = ''.join([word for word in text if word not in string.punctuation])

        return text

    def talking_to_me(self, text):
        text = text.lower()

        regex = re.search(r'(^e+r+i+\s+)|(\s+e+r+i+$)|(\s+e+r+i+\s+)', text)

        if regex:
            return True

        return False

    def recognize(self, text):
        min_distance = 9999
        index = 0

        text = self.clear_string(text)

        for i in range(len(self.dictionary)):
            question = self.dictionary[i][0]
            distance = Levenshtein.distance(question, text)

            if distance < min_distance:
                min_distance = distance
                index =  i

        answer = self.dictionary[index][1]

        if isinstance(answer, list):
            answer = random.choice(answer)

        return answer

if __name__ == "__main__":
    conversation = Conversation()

    conversation.load_dictionary("intentions.yml")
    conversation.load_dictionary("dialogs.yml")

    while True:
        text = input("Di algo: ")
        answer = conversation.recognize(text)

        print("Prediction: %s" %(answer))
