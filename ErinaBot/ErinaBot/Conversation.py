import re
import yaml
import time
import string
import random
import unidecode
import Levenshtein

from discord import Embed, Color

intention_callbacks = {}
intentions_help = []


class Arguments():

    def __init__(self, content):
        self.string = None
        self.number = None
        self.yt_url = None

        regex1 = re.search(r'(\'|\")(.*)(\'|\")', content)
        regex2 = re.search(r'([0-9]+)', content)
        regex3 = re.search(
            r'(https?://)?(www\.)?'
            '(youtube|youtu|youtube-nocookie)\.(com|be)/'
            '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})', content)

        if regex1:
            self.string = regex1.group(2)

        if regex2:
            self.number = int(regex2.group(1))

        if regex3:
            self.yt_url = "http://www.youtube.com/watch?v=%s" %(regex2.group(6))


class Intention():

    def __init__(self, callback, condition):
        self.callback = callback
        self.condition = condition

    async def call(self, condition, message, args):
        if condition ==  self.condition:
            await self.callback(message, args)


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

    def set_context_var(self, ctx, var, val):
        key = "%s.%s" %(ctx.channel.id, var)
        self.context[key] = val

    def get_context_var(self, ctx, var):
        key = "%s.%s" %(ctx.channel.id, var)
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
        text = re.sub(r'(\"|\')(.+)(\"|\')', "", text)
        text = re.sub(r'([0-9]+)', "", text)
        text = re.sub(r'(^e+r+i+\s+)|(\s+e+r+i+$)|(\s+e+r+i+\s+)', "", text)
        text = re.sub(
                r'(https?://)?(www\.)?'
                '(youtube|youtu|youtube-nocookie)\.(com|be)/'
                '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})', "", text)

        text = ''.join([word for word in text if word not in string.punctuation])

        return text

    def talking_to_me(self, text):
        text = text.lower()

        regex = re.search(r'(^e+r+i+\s+)|(\s+e+r+i+$)|(\s+e+r+i+\s+)', text)

        if regex:
            return True

        return False

    async def recognize(self, msg):
        min_distance = 9999
        index = 0

        text = self.clear_string(msg.content)

        for i in range(len(self.dictionary)):
            question = self.dictionary[i][0]
            distance = Levenshtein.distance(question, text)

            if distance < min_distance:
                min_distance = distance
                index =  i

        intention = self.dictionary[index][1]

        if intention == 'help':
            for help in intentions_help:
                embed = Embed(description=help,
                                color=Color.purple())

                await msg.channel.send(embed=embed)
                time.sleep(1)

            return

        if isinstance(intention, list):
            answer = random.choice(intention)
            await msg.channel.send(answer)

        else:
            if not intention in intention_callbacks.keys():
                print("ConversationError: recognized intention '%s' is not implemented" %(intention))
                return

            print("Recognized intention: %s" %(intention))
            await intention_callbacks[intention](msg, Arguments(msg.clean_content))


def handle_intention(func):
    intention_callbacks[func.__name__] = func
    if func.__doc__:
        intentions_help.append(func.__doc__)

    return func

if __name__ == "__main__":
    conversation = Conversation()

    conversation.load_dictionary("intentions.yml")
    conversation.load_dictionary("dialogs.yml")

    while True:
        text = input("Di algo: ")
        answer = conversation.recognize(text)

        print("Prediction: %s" %(answer))
