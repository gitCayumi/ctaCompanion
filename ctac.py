from app import app, db
from app.models import User, Post, Hero, Base

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'Hero': Hero, 'Base': Base}