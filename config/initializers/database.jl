using Mongoc

client = Mongoc.Client(MongoDB_URI)
Mongoc.ping(client)