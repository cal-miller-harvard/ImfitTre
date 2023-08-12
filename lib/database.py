import re
from io import BytesIO
import numpy as np

async def load_shot(db, id, require_image=False):
    """Returns the database entry for a given shot. If no shot is give, returns the most recent shot.

    Args:
        db: The database to query.
        id (None or string): The shot to return, in the format YYYY_MM_DD_shotnumber. If None, returns the most recent shot.
        require_image (bool): If True, raises an error if the shot does not have images. If the shot is not specified, the most recent shot with images is returned if True.
    """

    if id is not None:
        if not re.match(r'^\d{4}_\d{2}_\d{2}_\d+$', id):
            raise ValueError('Invalid shot format. Please use YYYY_MM_DD_shotnumber.')
        data = await db.shots.find_one({'_id': id})
        if require_image and 'images' not in data:
            raise ValueError('Shot {} does not have images.'.format(id))
    elif require_image:
        data = await db.shots.find_one({'images': {'$exists': True}}, sort=[('time', -1)])
    else:
        data = await db.shots.find_one(sort=[('time', -1)])

    if data is None:
        raise ValueError('Shot {} not found.'.format(id))
    
    return data

async def load_images(db, fs, id, camera=None):
    """Returns the images for a given shot. If no shot is give, returns the images from the most recent shot with images.
    
    Args:
        db: The database to query.
        fs: The gridfs to query.
        id (None or string): The shot to return, in the format YYYY_MM_DD_shotnumber. If None, returns the most recent shot.
        camera (None or string): The camera whose images to return. If None, returns images from all cameras.

    Returns:
        (dict, dict): A tuple of dictionaries. The first dictionary maps camera names to numpy arrays of images. The second dictionary is the database entry for the shot.

    """
    shot_data = await load_shot(db, id, require_image=True)
        
    cameras = {}
    for (k,v) in shot_data["images"].items():
        if camera is None or camera == k:
            id = v["imageID"]
            metadata = await db["fs.files"].find_one({"_id": id})
            dtype = metadata["dtype"]
            shape = metadata["shape"]
            
            with BytesIO() as output:
                await fs.download_to_stream(id, output)
                output.seek(0)
                cameras[k] = np.frombuffer(output.read(), dtype=dtype).reshape(shape)
    return cameras, shot_data