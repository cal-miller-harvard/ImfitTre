from quart import Blueprint, render_template, redirect
from quart import current_app as app

home_bp = Blueprint(
    'home_bp',
    __name__, 
    template_folder='templates',
)

@home_bp.route('/')
async def dashboard():
    return await render_template('dashboard.html')

@home_bp.route('/favicon.ico')
async def favicon():
    return redirect('/static/favicon.ico')