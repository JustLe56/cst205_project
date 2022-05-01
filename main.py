# Uses https://stackoverflow.com/questions/68945080/pytube-exceptions-regexmatcherror-get-throttling-function-name-could-not-find?answertab=modifieddesc#tab-top
# Above link gets around get throttling function_name could not find match for multiple
# Go to your env folder into /lib/pythonX.X/site-packages/pytube and you will find the mentioned file from the SO post.
from flask import Flask, render_template, redirect, url_for, request, send_file
from io import BytesIO
from pytube import YouTube
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
    return render_template("landing.html")

# home route
@app.route('/home', methods=('GET','POST'))
def home():
    form = query()
    if form.validate_on_submit():
        update_url(form.url.data) 
        return redirect(url_for('download_playlist'), code=307)
    return render_template("home.html", form=form)

# download playlist route
@app.route('/download/playlist' , methods=['GET', 'POST'])
def download_playlist():
    print(f"method: {request.method}")
    if request.method == "POST":
        buffer = BytesIO() # Declaring the buffer
        url = YouTube(stored_url[0]) # Getting the URL
        #itag = request.form.get("itag") # Get the video resolution 
        video = url.streams.filter(file_extension='mp4')[0] # Store the video into a variable
        video.stream_to_buffer(buffer)
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name="Video - YT2Video.mp4", mimetype="video/mp4")
    return redirect(url_for("home"))

    return render_template('result.html', link=stored_url[0])


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('home'))
    return render_template('login.html', error=error)

@app.route('/profile')
def profile():
    return 'Welcome User'
