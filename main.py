from flask import Flask, render_template, flash, redirect
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

# home route
@app.route('/', methods=('GET','POST'))
def home():
    form = query()
    if form.validate_on_submit():
        update_url(form.url.data) 
        return redirect('/download/playlist')
    return render_template("home.html", form=form)

# download playlist route
@app.route('/download/playlist')
def download_playlist():
    print(f'url: {stored_url}')
    return render_template('result.html', video=stored_url[0])
