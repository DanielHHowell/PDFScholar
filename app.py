# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename  # from flask.ext.sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
import os
import secrets
import stat
from tika import parser

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
app.secret_key = secrets.token_urlsafe(16)

UPLOAD_FOLDER = '/home/daniel/PycharmProjects/pdfscholar/files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024

app.jinja_env.lstrip_blocks = False
app.jinja_env.trim_blocks = False
app.jinja_env.keep_trailing_newline = False

basedir = os.path.abspath(os.path.dirname(__file__))

ALLOWED_EXTENSIONS = set(['TXT', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# db = SQLAlchemy(app)

# Automatically tear down SQLAlchemy.
'''
@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()
'''

# Login required decorator.
'''
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap
'''


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def home():
    itemList = os.listdir(UPLOAD_FOLDER)
    return render_template('pages/home.html', itemList=itemList)


@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        pathloc = os.path.join(app.config['UPLOAD_FOLDER'], 'PDF', file.filename)
        file.save(pathloc)
        processed = parser.from_file(pathloc)['content']
        txtname = file.filename.split('.')[0] + '.txt'
        with open(os.path.join(app.config['UPLOAD_FOLDER'], 'TXT', txtname), 'w+') as fw:
            fw.write(processed)
    return redirect('/')


# if file.filename == '':
# 	flash('No file selected for uploading')
# 	return redirect(request.url)
# if file and allowed_file(file.filename):
#     #filename = secure_filename(file.filename)
#     file = textract.process(file.read())
#     file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'TXT', file.filename))
#     return redirect('/')
# else:
# 	flash('Allowed file types are TXT, pdf, png, jpg, jpeg, gif')
# 	return redirect(request.url)

@app.route('/browser/<path:urlFilePath>')
def browser(urlFilePath):
    nestedFilePath = os.path.join(UPLOAD_FOLDER, urlFilePath)
    if os.path.isdir(nestedFilePath):
        itemList = os.listdir(nestedFilePath)
        fileProperties = {"filepath": nestedFilePath}
        if not urlFilePath.startswith("/"):
            urlFilePath = "/" + urlFilePath
        return render_template('pages/home.html', urlFilePath=urlFilePath, itemList=itemList)
    if os.path.isfile(nestedFilePath):
        if not urlFilePath.startswith("/"):
            urlFilePath = "/" + urlFilePath
        with open(nestedFilePath, 'r') as f:
            text = f.read()
            groups = text.split("\n")
            paragraphs = [i.replace("\n", "") for i in groups if (i != "")]
            for i in range(5):
                for i, j in enumerate(paragraphs):
                    if (j[-1] == ' ') or (j[-1] == '-'):
                        paragraphs[i:i + 2] = [''.join(paragraphs[i:i + 2])]
        return render_template('pages/file.html', text=paragraphs)
    return 'something bad happened'


# Error handlers.


@app.errorhandler(500)
def internal_error(error):
    # db_session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
