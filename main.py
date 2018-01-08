from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'IDQ5zpZfPBmd'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'list_blogs', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect ('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    username_error = ""
    password_error = ""
    blanks_error = ""
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        def blanks(field):
            return field == ''

        def too_short(field):
            return len(field) < 3

        def mismatch(password, verify):
            return password != verify

        if blanks(username) == True or blanks(password) == True or blanks(verify) == True:
            flash('One or more fields were left blank. Please fill out all fields.', 'error')
            blanks_error = True

        if too_short(username) == True:
            username_error = 'Username must be at least 3 characters.'

        if too_short(password) == True:
            password_error = 'Password must be at least 3 characters.'

        if mismatch(password, verify) == True:
            password_error = 'The password and verify password field entries must match.'

        if username_error != '' or password_error != '' or blanks_error != '':
            return render_template('signup.html', title='Signup', username=username, password_error=password_error, username_error=username_error)

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        
        else:
            flash('That username already exists. Please choose another.', 'error')
            return render_template('signup.html', title='Signup', username=username, password_error=password_error, username_error=username_error)


    return render_template('signup.html', title='Signup')

@app.route('/logout')
def logout():
    del session['username']
    flash("Logged Out")
    return redirect('/blog')

@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()

    return render_template('index.html', title="Blog Users!", users=users)

@app.route('/blog')
def list_blogs():
    userId = request.args.get('user')
    id = request.args.get('id')
    blogs = Blog.query.all()
    users = User.query.all()

    if id != None:
        blog = find_blog_by_id(id, blogs)
        return render_template('post.html', title=blog.title, post=blog)
    elif userId != None:
        blogs_by_user = find_blogs_by_user(userId, blogs)
        user = find_user_by_id(userId, users)
        return render_template('blogs.html', title=user.username + "'s Blog", blogs=blogs_by_user)
    else:
        return render_template('blogs.html', title='Blog Posts', blogs=blogs)

def find_blog_by_id(id, blogs):
    result = None
    for blog in blogs:
        if blog.id == int(id):
            result=blog 
            break;

    return result

def find_user_by_id(userId, users):
    result = None
    for user in users:
        if user.id == int(userId):
            result=user
            break;

    return result

def find_blogs_by_user(userId, blogs):
    result = []
    for blog in blogs:
        if blog.owner.id == int(userId):
            result.append(blog)

    return result

@app.route('/newpost')
def display_newpost_form():
    return render_template('newpost.html', title='New Post')

def is_empty(entry):
    return entry == ""

@app.route('/newpost', methods=['POST'])
def newpost():
    owner = User.query.filter_by(username=session['username']).first()
    title_error = ""
    content_error = ""

    if request.method == 'POST':
        blog_title = request.form['blog_title']
        body = request.form['body']

        new_blog = Blog(blog_title, body, owner)

        if is_empty(blog_title):
            title_error = "You must enter a title."
        
        if is_empty(body):
            content_error = "You must include content in the body of your post."
        
        if title_error == "" and content_error == "":
            db.session.add(new_blog)
            db.session.commit()
            id = new_blog.id

            return redirect('/blog?id='+str(id))
        else:
            return render_template("newpost.html", title="New Post", title_error=title_error, content_error=content_error, blog_title=blog_title, body=body)

    return render_template('blogs.html', title="Build a Blog!")

if __name__ == '__main__':
    app.run()