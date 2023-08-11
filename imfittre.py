from quart import Quart, Response
from quart_mongo import Mongo
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from io import BytesIO

import json
import re
import numpy as np
import base64
from PIL import Image

# Load secrets
with open('secrets.json', 'r') as f:
    secrets = json.load(f)

app = Quart(__name__)
mongo = Mongo(app, secrets['mongo_uri'])

@app.route('/')
async def hello():
    return 'Hello, world!'

@app.route('/shot', defaults={'shot_id': None})
@app.route('/shot/<shot_id>')
async def shot(shot_id):
    """Returns the database entry for a given shot. If no shot is give, returns the most recent shot.

    Args:
        shot_id (None or string): The shot to return, in the format YYYY_MM_DD_shotnumber. If None, returns the most recent shot.
    """

    if shot_id is not None:
        if not re.match(r'^\d{4}_\d{2}_\d{2}_\d+$', shot_id):
            return 'Invalid shot format. Please use YYYY_MM_DD_shotnumber.'
        data = await mongo.db.shots.find_one({'_id': shot_id})
    else:
        data = await mongo.db.shots.find_one(sort=[('time', -1)])

    if data is None:
        return 'Shot not found.'
    return data

@app.route('/image', defaults={'shot_id': None})
@app.route('/image/<shot_id>')
async def image(shot_id):
    """Displays the images for a given shot. If no shot is give, returns images from the most recent shot.

    Args:
        shot (None or string): The shot to display, in the format YYYY_MM_DD_shotnumber. If None, returns images from the most recent shot.
    """
    if shot_id is not None:
        shot_data = await shot(shot_id)
    else:
        # get the latest shot that has images
        shot_data = await mongo.db.shots.find_one({'images': {'$exists': True}}, sort=[('time', -1)])
        
    frames = {}
    for (k,v) in shot_data["images"].items():
        id = v["imageID"]
        metadata = await mongo.db["fs.files"].find_one({"_id": id})
        dtype = metadata["dtype"]
        shape = metadata["shape"]

        print("dtype: " + dtype + ", shape: " + str(shape))
        
        fs = AsyncIOMotorGridFSBucket(mongo.db)
        with BytesIO() as output:
            await fs.download_to_stream(id, output)
            output.seek(0)
            frames[k] = np.frombuffer(output.read(), dtype=dtype).reshape(shape)

    html = "<html><body>"
    html += """<meta http-equiv="refresh" content="30" />"""
    # html += """<script src="/path/to/htmx.min.js"></script>"""
    for (k, v) in frames.items():
        html += "<h1>" + shot_data["_id"] +" "+ k + "</h1>"
        for i in range(v.shape[0]):
            rescaled = (255.0 / v[i].max() * (v[i] - v[i].min())).astype(np.uint8)
            im = Image.fromarray(rescaled)
            with BytesIO() as output:
                im.save(output, format="PNG")
                contents = output.getvalue()
                encoded = base64.b64encode(contents).decode("utf-8")
                html += "<img src='data:image/png;base64," + encoded + "'/>"
    html += "</body></html>"
    return Response(html, content_type='text/html')

if __name__ == '__main__':
    app.run(debug=True)
