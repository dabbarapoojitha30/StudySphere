from pymongo import MongoClient

client = MongoClient("mongodb+srv://poojitha:1234@cluster0.dlniq2s.mongodb.net/")

db = client["StudySphere"]