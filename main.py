from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash


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
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    username = db.Column(db.String(120))
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.pw_hash = make_pw_hash(password)

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
            if check_pw_hash(password, user.pw_hash):
                session['username'] = user.username
                flash('Welcome back, '+ user.username)
                return redirect("/newpost")
            else:
                password_error = 'Password is incorrect.'
        else:
            username_error = 'This username does not exist.'
    return render_template('login.html', username=username, password_error=password_error, username_error=username_error)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    email = ''
    email_error = ''
    password_error = ''
    verify_error = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        username_error = ''
        password_error = ''
        verify_error = ''
        email_db_count = User.query.filter_by(email=email).count()


        if not is_email(email):
            email_error = 'Zoiks! "' + email + '" does not seem like an email address.'
        elif email_db_count > 0:
            email_error = 'Yikes! "' + email + '" is already taken and password reminders are not implemented.'
        elif len(email) < 3:
            email_error = 'Password must be at least 3 characters.'
        if not password:
            password_error = 'You must enter a password.'
        elif len(password) < 3:
            password_error = 'Password my be at least 3 characters.'
        elif password != verify:
            verify_error = 'Passwords did not match.'
        if not email_error and not password_error and not verify_error:
            end = int(email.find('@'))
            username = email[0:end]
            user = User(email, username, password)
            db.session.add(user)
            db.session.commit()
            session['username'] = user.username
            return redirect("/newpost")
    return render_template('signup.html', email=email, email_error=email_error, password_error=password_error, verify_error=verify_error)

def is_email(string):
    atsign_index = string.find('@')
    atsign_present = atsign_index >= 0
    if not atsign_present:
        return False
    else:
        domain_dot_index = string.find('.', atsign_index)
        domain_dot_present = domain_dot_index >= 0
        return domain_dot_present

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', title = 'Home', users=users)

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
    if request.args.get('user'):
        user_id = request.args.get('user')
        owner = User.query.get(user_id)
        blogs = Blog.query.filter_by(owner=owner)
        return render_template('singleUser.html', title="Blog Posts", blogs=blogs)
    blogs = Blog.query.all()    
    return render_template('blog.html', title="Build A Blog", blogs=blogs)

endpoints_without_login = ['login', 'signup', 'blog', 'view', 'index']

@app.before_request
def require_login():
    if not ('username' in session or request.endpoint in endpoints_without_login):
        return redirect("/login")

@app.route('/newpost', methods=['GET', 'POST'])
def newpost():    
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
        
        return render_template('add_post.html', title="Add A Post", 
        title_error=title_error, body_error=body_error, 
        blog_title=blog_title, blog_body=blog_body)
    return render_template('add_post.html', title="Add A Post")

@app.route('/view')
def view():
    id = request.args.get('id')
    blog = Blog.query.get(id)
    return render_template('view_post.html', blog=blog)

if __name__ == '__main__':    
    app.run()