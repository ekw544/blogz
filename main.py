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

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/blog')
def index():
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
    blog_title = request.form['blog_title']
    body = request.form['body']
    new_blog = Blog(blog_title, body)

    title_error = ""
    content_error = ""
    
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

if __name__ == '__main__':
    app.run()