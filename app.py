# -*- coding: utf-8 -*-
import json
import os
import requests
from flask import Flask, request, url_for, send_from_directory, render_template, flash
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpeg', 'gif'}

app = Flask(__name__)
app.secret_key = '\x83X?\xe61\x01]\xc5\xee\xfc\x90\xf9F\x0ft\xc4\x16\x9eB\xffL\xdf\xa9"'
app.config['UPLOAD_FOLDER'] = os.getcwd() + '/static/img'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def get_access_token():
    url = 'https://volumental.eu.auth0.com/oauth/token'
    data = json.dumps({"client_id": "yAdjPKiLQyK2ujTj6XcTC7lQy1GYq0Po",
                       "client_secret": "h-wu0HuXbIOToBUbEnzBdvsH-9YkjY3eov10gbAgwG6HZ0-ksH7h9DrVa17b8QB2",
                       "audience": "http://homeexercise.volumental.com/", "grant_type": "client_credentials"})
    r = requests.post(url, headers={'Content-Type': 'application/json'}, data=data)
    return r.json()['access_token']


def get_colors(file):
    token = 'Bearer ' + get_access_token()
    url = ' https://homeexercise.volumental.com/colors/images'
    data = open(file, 'rb').read()
    res = requests.post(url, data=data,
                        headers={'Content-Type': 'application/octet-stream', 'Authorization': token})
    return res.json()


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash("Please select a picture and upload", "danger")
            return render_template('upload.html')
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash("Please select a picture and upload", "danger")
            return render_template('upload.html')
        # if user does not upload 'png', 'jpeg' or 'gif'
        if not allowed_file(file.filename):
            flash("Please upload image of PNG, JPEG or GIF", "danger")

        if file and allowed_file(file.filename):
            flash("Upload successfully!", "success")
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_url = url_for('uploaded_file', filename=filename)
            colors = get_colors('static/img/' + filename)
            return render_template('image.html', file_url=file_url, colors=colors)

    return render_template('upload.html')


if __name__ == '__main__':
    app.run()
