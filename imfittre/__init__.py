from quart import Quart
from quart_mongo import Mongo
from quart_cors import cors
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from influxdb_flask import InfluxDB

from config import Config

mongo = Mongo()
influx_db = InfluxDB()

async def init_app():
    """Create Flask application."""
    app = Quart(__name__)
    app = cors(app, allow_origin="*")
    app.config.from_object(Config)

    mongo.init_app(app)
    influx_db.init_app(app)

    async with app.app_context():
        # Import parts of our application
        from imfittre.data import data
        from imfittre.fit import fit
        from imfittre.home import home

        # Register Blueprints
        app.register_blueprint(data.data_bp)
        app.register_blueprint(fit.fit_bp)
        app.register_blueprint(home.home_bp)

        return app
