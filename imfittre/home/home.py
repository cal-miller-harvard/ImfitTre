from quart import Blueprint, redirect, send_from_directory
from quart import current_app as app

home_bp = Blueprint(
    'home_bp',
    __name__, 
    template_folder='templates',
)

# Path for our main Svelte page
@app.route("/")
def base():
    return send_from_directory('client/build', 'index.html')

# Path for all the static files (compiled JS/CSS, etc.)
@app.route("/<path:path>")
def home(path):
    return send_from_directory('client/build', path)