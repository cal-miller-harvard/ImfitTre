from quart import Blueprint, request
from quart import current_app as app
from motor.motor_asyncio import AsyncIOMotorGridFSBucket

from imfittre.fit import image_fit as imfit
from imfittre import calibrations
from imfittre.data import database as db

from .. import mongo

fit_bp = Blueprint(
    'fit_bp',
    __name__
)

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
            await fit_shot(change["documentKey"]["_id"], update_db=True)

@fit_bp.before_app_serving
async def create_fs():
    global fs
    fs = AsyncIOMotorGridFSBucket(mongo.db)
    app.add_background_task(watch_shots)

async def fit_shot(shot_id, config=None, update_db=False):
    if config is None:
        config = calibrations.default_fit

    images, data = await db.load_images(mongo.db, fs, shot_id)
    result = imfit.fit(images, data, config)

    shot_id = data["_id"]

    if update_db:
        # only replace the fit."name".result subdocument
        update = {"fit.{}.result".format(k): v  for k, v in result.items()}
        await db.update_shot(mongo.db, shot_id, update)

    return result

@fit_bp.route('/fit', methods=["GET", "POST"])
async def fit():
    shot_id = request.args.get('shot_id', None)
    update_db = request.args.get('update_db', False)

    # if post request, get config from json
    if request.method == "POST":
        config = await request.get_json()
    else:
        config = calibrations.default_fit

    result = await fit_shot(shot_id, config, update_db)
    return result
