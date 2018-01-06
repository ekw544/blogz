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
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    # blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect ('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/')

        else:
            return "<h1>Duplicate user</h1>"

    return render_template('register.html')

@app.route('/logout')
def logout():
    del session['email']
    flash("Logged Out")
    return redirect('/')

@app.route('/', methods=['POST', 'GET'])
def index():
    owner = User.query.filter_by(email=session['email']).first()

    if request.method == 'POST':
        blog_title = request.form['blog_title']
        body = request.form['body']

        new_blog = Blog(blog_title, body, owner)
        db.session.add(new_blog)
        db.session.commit()

    return render_template('blogs.html', title="Build a Blog!")

@app.route('/blog')
def index2():
    id = request.args.get('id')
    blogs = Blog.query.all()
    if id != None:
        blog = find_blog_by_id(id, blogs)
        return render_template('post.html', title=blog.title, blogs=blog)
    else:
        return render_template('blogs.html', title='Blog Posts', blogs=blogs)

def find_blog_by_id(id, blogs):
    result = None
    for blog in blogs:
        if blog.id == int(id):
            result=blog 
            break;

    return result

@app.route('/newpost')
def display_newpost_form():
    return render_template('newpost.html', title='New Post')

def is_empty(entry):
    return entry == ""

@app.route('/newpost', methods=['POST'])
def newpost():
    owner = User.query.filter_by(email=session['email']).first()
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