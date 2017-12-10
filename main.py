from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
# app.secret_key = 'WRZeIDQ5zpZfPBmdWRZeIDQ5zpZfPBmd'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    #owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    #def __init__(self, title, owner):
    def __init__(self, title, body):
        self.title = title
        self.body = body
        #self.completed = False
        #self.owner = owner

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(120), unique=True)
#     password = db.Column(db.String(120))
#     #blogs = db.relationship('Blog', backref='owner')
    
#     def __init__(self, email, password):
#         self.email = email
#         self.password = password

# @app.before_request
# def require_login():
#     allowed_routes = ['login', 'register']
#     if request.endpoint not in allowed_routes and 'email' not in session:
#         return redirect('/login')


# @app.route('/login', methods=['POST', 'GET'])
# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         user = User.query.filter_by(email=email).first()
#         if user and user.password == password:
#             session['email'] = email
#             flash("Logged in")
#             return redirect('/')
#         else:
#             flash('User password incorrect, or user does not exist', 'error')

#     return render_template('login.html')

# @app.route('/register', methods=['POST', 'GET'])
# def register():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         verify = request.form['verify']

#         # TODO - validate user's data
#         session['email'] = email

#         existing_user = User.query.filter_by(email=email).first()
#         if not existing_user:
#             new_user = User(email, password)
#             db.session.add(new_user)
#             db.session.commit()
#             # TODO - "remember" the user
#             return redirect('/')
#         else:
#             # TODO - user better reponse messaging
#             return '<h1>Duplicate user</h1>'


#     return render_template('register.html')

# @app.route('/logout')
# def logout():
#     del session['email']
#     return redirect('/')

# @app.route('/')
# def index():
#     # return render_template("blogs.html", title="Build a Blog!", blogs=blogs)
#     return render_template("blogs.html", title="Build a Blog!")

# @app.route('/delete-blog', methods=['POST'])
# def delete_blog():
#     blog_id = int(request.form['blog-id'])
#     blog = Blog.query.get(blog_id)
#     blog.completed = True
#     db.session.add(blog)
#     db.session.commit()

#     return redirect('/')


@app.route('/blog')
def index():
    # blog_title = request.form['blog_title']
    # body = request.form['body']
    # new_blog = Blog(blog_title, body)
    # blog = Blog.query.get(blog_id)
    # blog.completed = True
    # db.session.add(blog)
    # db.session.commit()

    # db.session.add(new_blog)
    # db.session.commit()
    blogs = Blog.query.all()
    return render_template('blogs.html', title='Blog Posts', blogs=blogs)
    # return redirect('/')

@app.route('/newpost')
def display_newpost_form():
    return render_template('newpost.html', title='New Post')

def is_empty(entry):
    return entry == ""

@app.route('/newpost', methods=['POST'])
def newpost():
    blog_title = request.form['blog_title']
    body = request.form['body']
    new_blog = Blog(blog_title, body)

    title_error = ""
    content_error = ""
    
    if is_empty(blog_title):
        title_error = "You must enter a title."
    
    if is_empty(body):
        content_error = "You must include content in the body of your post."
    
    # if request.method == 'GET':
    #     return render_template('newpost.html', title='New Post', blogs=blogs)
    
    if title_error == "" and content_error == "":
        db.session.add(new_blog)
        db.session.commit()

        return redirect('/blog')
    else:
        return render_template("newpost.html", title="New Post", title_error=title_error, content_error=content_error, blog_title=blog_title, body=body)
    

if __name__ == '__main__':
    app.run()