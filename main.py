from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:19thisIsthepw93@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'gy5pLKK8L'
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    blog_body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, blog_body, owner):
        self.title = title
        self.blog_body = blog_body
        self.owner_id = owner.id

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_error = ''
        username_error = ''
        users = User.query.filter_by(username=username)
        if users.count() == 1:
            user = users.first()
            if password == user.password:
                session['username'] = user.username
                flash('Welcome back, '+ user.username)
                return redirect("/newpost")
            else:
                password_error = 'Password is incorrect.'
        else:
            username_error = 'This username does not exist.'
    return render_template('login.html', password_error=password_error, username_error=username_error)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        username_error = ''
        password_error = ''
        verify_error = ''
#TODO take away flashes and add errors to be input instead.

        if not is_email(username):
            flash('zoiks! "' + username + '" does not seem like an email address')
            return redirect('/register')
        email_db_count = User.query.filter_by(username=username).count()
        if email_db_count > 0:
            flash('yikes! "' + username + '" is already taken and password reminders are not implemented')
            return redirect('/register')
        if password != verify:
            flash('passwords did not match')
            return redirect('/register')
        if not password:
            flash('you must enter a password.')
            return redirect('/register')
        if len(password) < 3 or len(username) < 3:
            flash('Username and password must be ')
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        session['user'] = user.username
        return redirect("/")
    else:
        return render_template('signup.html')

def is_email(string):
    atsign_index = string.find('@')
    atsign_present = atsign_index >= 0
    if not atsign_present:
        return False
    else:
        domain_dot_index = string.find('.', atsign_index)
        domain_dot_present = domain_dot_index >= 0
        return domain_dot_present

@app.route('/index')
def index():
    return render_template('index.html')

@app.route("/logout", methods=['POST'])
def logout():
    del session['username']
    return redirect("/blog")

@app.route('/blog', methods=['GET'])
def blog():
    if request.args.get('id'):
        id = request.args.get('id')
        blog = Blog.query.get(id)
        return render_template('view_post.html', blog=blog)

    blogs = Blog.query.all()
    return render_template('blog.html', title="Build A Blog", blogs=blogs)

endpoints_without_login = ['login', 'signup', 'blog', 'view', 'index']

@app.before_request
def require_login():
    if not ('user' in session or request.endpoint in endpoints_without_login):
        return redirect("/register")

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
            owner = User.query.filter_by(username=session['username']).first()
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            id = str(new_blog.id)
            return redirect("/view?id=" + id)
        
        else:
            return render_template('add_post.html', title="Add A Post",
                title_error=title_error, body_error=body_error, 
                blog_title=blog_title, blog_body=blog_body)

@app.route('/newpost')
def add_home():
    return render_template('add_post.html', title="Add A Post")

@app.route('/view')
def view():
    id = request.args.get('id')
    blog = Blog.query.get(id)
    return render_template('view_post.html', blog=blog)

@app.route('/')
def home():
    return render_template('home.html', title="Welcome!")

if __name__ == '__main__':    
    app.run()