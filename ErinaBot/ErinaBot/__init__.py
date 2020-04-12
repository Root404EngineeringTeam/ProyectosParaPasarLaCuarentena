import pymongo

from discord import Webhook, RequestsWebhookAdapter

client_id = ""
access_token = ""

from . import Utils
from . import MusicPlayer
from . import Conversation

mongo = pymongo.MongoClient("mongodb://localhost:27017/")
db = mongo.ErinaBot

utils = Utils
music = MusicPlayer.MusicPlayer()
intention = Conversation.handle_intention
conversation = Conversation.Conversation()

conversation.load_dictionary("./ErinaBot/intentions.yml")
conversation.load_dictionary("./ErinaBot/dialogs.yml")
