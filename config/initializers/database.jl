using Mongoc

client = Mongoc.Client(MongoDB_URI)
Mongoc.ping(client)

db = client["data"]
collection = db["shots"]
bucket = Mongoc.Bucket(db)