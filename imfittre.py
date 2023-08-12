from quart import Quart, Response, redirect, request, abort, make_response, send_file, render_template
from quart_mongo import Mongo
from motor.motor_asyncio import AsyncIOMotorGridFSBucket

import json

import calibrations
import lib.image_process as ip
import lib.database as db
import lib.server_sent_events as sses

# TODO:
# Reorganize the code following https://hackersandslackers.com/flask-application-factory/
# Make the controls on the dashboard work
# Make the dashboard look nice
# Add controls for the view position and image range to the dashboard
# Add crosshairs to the images, whose position can be set by clicking or through the config or the dashboard
# Display the images in a prettier color scheme
# Add a display of the json data to the dashboard
# Fit the images
# Display the fit results
# Determine the schema for the fit configuration and results
# Load the fit results into the database

# Load secrets
with open('secrets.json', 'r') as f:
    secrets = json.load(f)

app = Quart(__name__)
mongo = Mongo(app, secrets['mongo_uri'])

async def watch_shots():
    """Watches the database for new shots and updates the list of shots."""
    async with mongo.db.shots.watch() as stream:
        async for change in stream:
            pass

@app.get("/new_shot")
async def sse():
    if "text/event-stream" not in request.accept_mimetypes:
        abort(400)

    async def send_events():
        async with mongo.db.shots.watch() as stream:
            async for change in stream:
                # data = change
                data = "new_shot"
                event = sses.ServerSentEvent(data, event="new_shot")
                yield event.encode()

    response = await make_response(
        send_events(),
        {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Transfer-Encoding': 'chunked',
        },
    )
    response.timeout = None
    return response

@app.before_serving
async def setup_database():
    global fs
    fs = AsyncIOMotorGridFSBucket(mongo.db)
    app.add_background_task(watch_shots)

@app.route('/')
async def dashboard():
    return await render_template('dashboard.html')

@app.route('/favicon.ico')
async def favicon():
    return redirect('/static/favicon.ico')

@app.route('/shot')
async def shot():
    shot_id = request.args.get('shot_id', None)
    return await db.load_shot(mongo.db, shot_id)

@app.route('/frame')
async def image():
    shot_id = request.args.get('shot_id', None)
    camera = request.args.get('camera')
    image = request.args.get('image', "|0,0>")
    type = request.args.get('type', "OD")
    max_val = request.args.get('max_val', None)
    min_val = request.args.get('min_val', None)
    dx = request.args.get('dx', None)
    dy = request.args.get('dy', None)

    config = calibrations.default_fit[image]

    images, data = await db.load_images(mongo.db, fs, shot_id, camera)

    if type == "OD":
        array = ip.calculateOD(images[camera], config)
    else:
        frame_num = config["frames"][type]
        array = ip.crop_frame(images[camera][frame_num], config)

    if dx is not None and dy is not None:
        size = (int(dx), int(dy))
    elif dx is not None:
        scale = int(dx) / array.shape[1]
        size = (int(array.shape[1]*scale), int(array.shape[0]*scale))
    elif dy is not None:
        scale = int(dy) / array.shape[0]
        size = (int(array.shape[1]*scale), int(array.shape[0]*scale))
    else:
        size = None

    output = ip.array_to_png(array, max_val, min_val, size)
    return await send_file(output, mimetype='image/png')

@app.route('/sse_test')
async def sse_test():
    html = """<html><body><script src="static\js\htmx.js"></script><script src="static\js\sse.js"></script>"""
    html += """ <div hx-ext="sse" sse-connect="/new_shot" sse-swap="new_shot">
      Contents of this box will be updated in real time
      with every SSE message received from the chatroom.
  </div>"""
    html += "</body></html>"
    return Response(html, content_type='text/html')

if __name__ == '__main__':
    app.run(debug=True)
