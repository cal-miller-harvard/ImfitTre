# ![Alt Text](imfittre/static/small_krab.png) ImfitTre 

Image analysis and display for the JILA KRb experiment as a replacement for [ImfitDue](https://github.com/krbjila/imfitDue).

Implemented using a [Quart](https://quart.palletsprojects.com/en/latest/) webserver and a [MongoDB](https://www.mongodb.com/) database.

To use, a config.py file must be created in the root directory with the following format:
```python
# config.py

class Config:
    QUART_MONGO_URI = "mongodb://localhost:27017/mydatabase"
