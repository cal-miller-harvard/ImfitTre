from quart import Quart
from quart_mongo import Mongo
from motor.motor_asyncio import AsyncIOMotorGridFSBucket

from config import Config

mongo = Mongo()

async def init_app():
    """Create Flask application."""
    app = Quart(__name__)
    app.config.from_object(Config)

    mongo.init_app(app)

    async with app.app_context():
        # Import parts of our application
        from imfittre.home import home
        from imfittre.data import data
        from imfittre.fit import fit

        # Register Blueprints
        app.register_blueprint(home.home_bp)
        app.register_blueprint(data.data_bp)
        app.register_blueprint(fit.fit_bp)

        return app
