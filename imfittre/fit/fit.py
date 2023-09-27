from quart import Blueprint, request, abort, make_response
from quart import current_app as app
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from influxdb_client.client.write_api import SYNCHRONOUS

from imfittre.fit import image_fit as imfit
from imfittre import calibrations
from imfittre.data import database as db
from imfittre.helpers.server_sent_events import ServerSentEvent


from asyncio import sleep

from .. import mongo, influx_db

fit_bp = Blueprint(
    'fit_bp',
    __name__
)

sse_queue = []

async def watch_shots():
    """Watches the database for new shots and updates the list of shots."""

    # TODO: This should be an update operation, but it seems it is a replace in the change stream. This works for now, but we should figure out why.
    pipeline = [{
            "$match": { 
                "$and": [
                    {"operationType": "replace"},
                    {"fullDocument.images": {"$exists": True}}
                ]
            }
        }]
    async with mongo.db.shots.watch(pipeline) as stream:
        async for change in stream:
            shot_id = change["documentKey"]["_id"]
            print("Fitting shot {}".format(shot_id))
            await fit_shot(shot_id, update_db=True)

@fit_bp.before_app_serving
async def create_fs():
    global fs
    fs = AsyncIOMotorGridFSBucket(mongo.db)
    app.add_background_task(watch_shots)

@fit_bp.route('/sse')
async def sse():
    if "text/event-stream" not in request.accept_mimetypes:
      abort(400)

    async def send_events():
        while True:
            while len(sse_queue) > 0:
                data = sse_queue.pop(0)
                event = ServerSentEvent(data)
                yield event.encode()
            await sleep(0.5)

    response = await make_response(
        send_events(),
        {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Transfer-Encoding": "chunked",
        },
    )
    response.timeout = None
    return response

async def fit_shot(shot_id, update_db=False):
    images, data = await db.load_images(mongo.db, fs, shot_id)
    config = {}
    for k in data.get("fit", {}):
        config[k] = data["fit"][k]["config"]
    result = imfit.fit(images, data, config)

    shot_id = data["_id"]

    if update_db:
        # only replace the fit."name".result subdocument
        update = {"fit.{}.result".format(k): v  for k, v in result.items()}
        await db.update_shot(mongo.db, shot_id, update)

        # also update influxdb
        # schema:
        #   bucket: log
        #   measurement: fit
        #   tags: fit name
        #   fields: derived.n, derived.sigmax_um, derived.sigmay_um, params.x0, params.y0
        #   time: now

        for k, v in result.items():
            try:
                write_api = influx_db.connection.write_api(write_options=SYNCHRONOUS)
                points = [{
                    "measurement": "fit",
                    "tags": {
                        "fit": k
                    },
                    "fields": {
                        "N": v["derived"]["N"] if "derived" in v and "N" in v["derived"] else None,
                        "sigmax_um": v["derived"]["sigmax_um"] if "derived" in v and "sigmax_um" in v["derived"] else None,
                        "sigmay_um": v["derived"]["sigmay_um"] if "derived" in v and "sigmay_um" in v["derived"] else None,
                        "x0_px": v["params"]["x0"] if "params" in v and "x0" in v["params"] else None,
                        "y0_px": v["params"]["y0"] if "params" in v and "y0" in v["params"] else None
                    }
                }]
                write_api.write(bucket="log", record=points)
            except KeyError as e:
                print(f"Error: {e} not found in {k} result")
                continue

        sse_queue.append(shot_id)

    return result

@fit_bp.route('/fit')
async def fit():
    shot_id = request.args.get('shot_id', None)
    update_db = request.args.get('update_db', False)

    result = await fit_shot(shot_id, update_db)
    return result
