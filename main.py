from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:19thisIsthepw93@localhost:3306/build_a_blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    blog_body = db.Column(db.String(500))

    def __init__(self, title, blog_body):
        self.title = title
        self.blog_body = blog_body



@app.route('/blog')
def blog():
    blogs = Blog.query.all()
    return render_template('blog.html', title="Build A Blog", blogs=blogs)


@app.route('/newpost', methods=['POST'])
def add():
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['blog_body']

        title_error = ""
        body_error = ""

        if (not blog_title) or (blog_title.strip() == ""):
            title_error = "Please fill in the title."
        
        if (not blog_body) or (blog_body.strip() == ""):
            body_error = "Please fill in the blog body."

        if (not title_error) and (not body_error):
            new_blog = Blog(blog_title, blog_body)
            db.session.add(new_blog)
            db.session.commit()
            return redirect("/blog")
        
        else:
            return render_template('add_post.html', title="Add A Post",
                title_error=title_error, body_error=body_error, 
                blog_title=blog_title, blog_body=blog_body)

@app.route('/newpost')
def add_home():
    return render_template('add_post.html', title="Add A Post")

@app.route('/')
def index():
    return render_template('home.html', title="Welcome!")

if __name__ == '__main__':    
    app.run()