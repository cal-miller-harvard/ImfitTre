from quart import current_app as app
from quart import Blueprint, request, send_file
from motor.motor_asyncio import AsyncIOMotorGridFSBucket

from imfittre.helpers import calibrations, image_process as ip, database as db
from .. import mongo

data_bp = Blueprint(
    'data_bp',
    __name__
)

async def watch_shots():
    """Watches the database for new shots and updates the list of shots."""
    async with mongo.db.shots.watch() as stream:
        async for change in stream:
            pass

@data_bp.before_app_serving
async def create_fs():
    global fs
    fs = AsyncIOMotorGridFSBucket(mongo.db)
    app.add_background_task(watch_shots)

@data_bp.route('/shot')
async def shot():
    shot_id = request.args.get('shot_id', None)
    return await db.load_shot(mongo.db, shot_id)


@data_bp.route('/frame')
async def frame():
    shot_id = request.args.get('shot_id', None)
    camera = request.args.get('camera')
    image = request.args.get('image', "|0,0>")
    type = request.args.get('type', "OD")
    max_val = request.args.get('max_val', None)
    min_val = request.args.get('min_val', None)
    cmap = request.args.get('cmap', "inferno")

    config = calibrations.default_fit[image]

    images, data = await db.load_images(mongo.db, fs, shot_id, camera)

    if type == "OD":
        array = ip.calculateOD(images[camera], config)
    else:
        frame_num = config["frames"][type]
        array = ip.crop_frame(images[camera][frame_num], config)

    output = ip.array_to_png(array, max_val, min_val, cmap)
    return await send_file(output, mimetype='image/png')
