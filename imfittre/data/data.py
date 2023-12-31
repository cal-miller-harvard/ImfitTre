from quart import current_app as app
from quart import Blueprint, request, send_file, abort, make_response
from motor.motor_asyncio import AsyncIOMotorGridFSBucket

from imfittre import calibrations
from imfittre.helpers import image_process as ip
from . import database as db

from .. import mongo

data_bp = Blueprint(
    'data_bp',
    __name__
)

@data_bp.before_app_serving
async def create_fs():
    global fs
    fs = AsyncIOMotorGridFSBucket(mongo.db)
    # app.add_background_task(watch_shots)

@data_bp.route('/shot')
async def shot():
    require_image = request.args.get('require_image', False)
    shot_id = request.args.get('shot_id', None)
    return await db.load_shot(mongo.db, shot_id, require_image)

@data_bp.route('/frame')
async def frame():
    shot_id = request.args.get('shot_id', None)
    camera = request.args.get('camera', None)
    image = request.args.get('image', "|0,0>")
    type = request.args.get('type', "OD")
    max_val = request.args.get('max_val', None)
    min_val = request.args.get('min_val', None)
    cmap = request.args.get('cmap', "inferno")
    show_fit = request.args.get('show_fit', False)
    width = request.args.get('width', None)
    height = request.args.get('height', None)

    if min_val is not None:
        min_val = float(min_val)
    if max_val is not None:
        max_val = float(max_val)
    if width is not None:
        width = int(width)
    if height is not None:
        height = int(height)

    images, data = await db.load_images(mongo.db, fs, shot_id, camera)

    if "fit" in data and image in data["fit"]:
        config = data["fit"][image]["config"]
    else:
        config = calibrations.default_fit[image]

    if camera is None:
        camera = list(images.keys())[0]

    if type == "OD":
        array = ip.calculateOD(images[camera], data["images"][camera], config)
    else:
        frame_num = config["frames"][type]
        array = ip.crop_frame(images[camera][frame_num], config)

    output = ip.array_to_png(array, max_val, min_val, cmap, width, height)
    
    if show_fit:
        fit = data["fit"][image]
        output = ip.fit_to_image(fit, background=output)

    return await send_file(output, mimetype='image/png')
