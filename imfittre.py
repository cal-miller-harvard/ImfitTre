from quart import Quart, Response
from quart_mongo import Mongo
from motor.motor_asyncio import AsyncIOMotorGridFSBucket

import json

import calibrations
import lib.image_process as ip
import lib.database as db

# Load secrets
with open('secrets.json', 'r') as f:
    secrets = json.load(f)

app = Quart(__name__)
mongo = Mongo(app, secrets['mongo_uri'])

@app.before_serving
async def create_gridfs_connection():
    global fs
    fs = AsyncIOMotorGridFSBucket(mongo.db)

@app.route('/')
async def hello():
    return 'Hello, world!'

@app.route('/shot', defaults={'shot_id': None})
@app.route('/shot/<shot_id>')
async def shot(shot_id):
    return await db.load_shot(mongo.db, shot_id)

@app.route('/image', defaults={'shot_id': None})
@app.route('/image/<shot_id>')
async def image(shot_id):
    images, data = await db.load_images(mongo.db, fs, shot_id)

    html = "<html><body>"
    if shot_id is None:
        html += """<meta http-equiv="refresh" content="30" />"""
    for (k, v) in images.items():
        html += "<h1>" + data["_id"] +" "+ k + "</h1>"
        for i in range(v.shape[0]):
            html += ip.np_to_html(v[i])
    html += "</body></html>"
    return Response(html, content_type='text/html')

@app.route('/od', defaults={'shot_id': None})
@app.route('/od/<shot_id>')
async def od(shot_id):
    images, data = await db.load_images(mongo.db, fs, shot_id)
    
    html = "<html><body>"
    if shot_id is None:
        html += """<meta http-equiv="refresh" content="30" />"""
    for (k, v) in images.items():
        for (mode, config) in calibrations.default_fit.items():
            html += "<h1>" + data["_id"] +" "+ k + " " + mode + "</h1>"
            img = ip.calculateOD(v, config)
            # determine the size of the image so the width is ~400px
            scale = 400 / img.shape[1]
            size = (int(img.shape[1]*scale), int(img.shape[0]*scale))
            html += ip.np_to_html(img, resize=size)
    html += "</body></html>"
    return Response(html, content_type='text/html')

if __name__ == '__main__':
    app.run(debug=True)
