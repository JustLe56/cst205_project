# Authors: Jose Barroso A., Justin Le, Runcheng Zheng
# Date: May 18, 2022
# Course: CST 205
# Title: YouTube Downloader
# Abstract: This program allows a pre-defined user to login and is 
        # then taken to their profile. From the profile the user can
        # see suggested videos to download or click a link to download
        # any video or playlist of their choice using a YouTube url. 

# Jose Barroso A: Worked on login page with authentication, profile page, and 
        # being able to navigate backwards.
# Justin Le: Worked on the API, being able to download the videos/playlists, and 
        # creating sessions.
# Runcheng Zheng: Worked setting up the html files and making the website look
        #  more appealing. 

# Github: https://github.com/JustLe56/cst205_project/tree/justin_download

# Trello: https://trello.com/b/NTL5ZdWY/cst205group7335

# Uses https://stackoverflow.com/questions/68945080/pytube-exceptions-regexmatcherror-get-throttling-function-name-could-not-find?answertab=modifieddesc#tab-top
# Above link gets around get throttling function_name could not find match for multiple
# Go to your env folder into /lib/pythonX.X/site-packages/pytube and you will find the mentioned file from the SO post.
# fixed as of pytube 12.1.0

# If you are on MacOS and getting CERTIFICATE_VERIFY_FAILED error
# use https://stackoverflow.com/questions/40684543/how-to-make-python-use-ca-certificates-from-mac-os-truststore#:~:text=cd%20/Applications/Python%5C%203.6/%0A./Install%5C%20Certificates.command

from flask import Flask, render_template, redirect, url_for, request, send_file, session
from io import BytesIO
import zipfile 
import os
from pytube import YouTube, Playlist
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


app = Flask(__name__)
app.config['SECRET_KEY'] = 'csumb-otter'
bootstrap = Bootstrap5(app)

#object for the query
class query(FlaskForm):
    url = StringField('url', validators=[DataRequired()])

#needs to be in an array for some reason;
#if just a string it seems to reset to inital value when redirected to new page
stored_url = []

#updates the stored url
def update_url(new_url):
    stored_url.append(new_url)

#initial landing page asking user to login/sign up
@app.route('/')
def landing():
    if session.get('username'):
        return redirect("/home")
    return render_template("landing.html")

# home route
@app.route('/home', methods=('GET','POST'))
def home():
    if not session.get('username'):
        return redirect("/login")
    return render_template("home.html")

# logout route
@app.route('/logout', methods=('GET','POST'))
def logout():
    session.clear()
    return redirect("/login")


# download single video route
@app.route('/download/video' , methods=['GET', 'POST'])
def download_video():
    if not session.get('username'):
        return redirect("/login")
    form = query()
    if request.method == "POST":
        if form.validate_on_submit():
            if ("watch" not in form.url.data):
                return render_template('download_video.html',form = form,error="Invalid video.")
            buffer = BytesIO() # Declaring the buffer
            user_video = YouTube(form.url.data) # Getting the URL
            video = user_video.streams.filter(file_extension='mp4')[0] # Store the video into a variable
            video_title = user_video.title
            video.stream_to_buffer(buffer)
            buffer.seek(0)
            return send_file(buffer, as_attachment=True, download_name=f"{video_title}.mp4", mimetype="video/mp4")
    return render_template('download_video.html',form = form,error=None)

# download playlist route
@app.route('/download/playlist' , methods=['GET', 'POST'])
def download_playlist():
    if not session.get('username'):
        return redirect("/login")
    form = query()
    if request.method == "POST":
        form = query()
        if form.validate_on_submit():
            update_url(form.url.data) 
            if ("playlist" not in form.url.data):
                return render_template('download_playlist.html',form = form,error="Invalid playlist.")
            filenames = []
            zip_path = "videos.zip"
            
            user_playlist = Playlist(form.url.data) # Getting the URL
            print(user_playlist.videos)
            #iterate over each video and download
            for index,video in enumerate(user_playlist.videos):
                video = video.streams.filter(file_extension='mp4')[0] # Store the video into a variable
                filenames.append(video.title)
                video.download()

            #iterate over each video and add to zipfile
            with zipfile.ZipFile(zip_path, mode="w") as archive:
                for filename in filenames:
                    archive.write(f'{filename}.mp4')
            
            #create buffer to store zip
            return_data = BytesIO()
            with open(zip_path, 'rb') as fo:
                return_data.write(fo.read())
            return_data.seek(0)

            #clean up downloaded files
            for file in filenames:
                os.remove(f'{file}.mp4')
            os.remove(zip_path)

            return send_file(return_data, as_attachment=True, download_name=f"playlist.zip")
    return render_template('download_playlist.html',form = form,error=None)

# Pre-defined user login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('username'):
        return redirect("/home")
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            session['username'] = request.form['username'] #update session with username
            return redirect(url_for('profile'))
    return render_template('login.html', error=error)

# Profile route
@app.route('/profile')
def profile():
    if not session.get('username'):
        return redirect("/login")
    return render_template('profile.html')

# View user's downloaded media route
@app.route('/my_downloads')
def downloaded():
    if not session.get('username'):
        return redirect("/login")
    return render_template('my_downloads.html')

