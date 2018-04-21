from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:cheese@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

#Classes---------------------------------------------------------------
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300))
    body = db.Column(db.String(5000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

    def __repr__(self):
        return '<Blog %r>' % self.title

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')
    
    def __init__(self, email, password):
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.email


#Handlers------------------------------------------------------------
endpoints_without_login = ['login', 'signup']

@app.before_request
def require_login():
    if not ('user' in session or request.endpoint in endpoints_without_login):
        return redirect("/login")

@app.route("/logout", methods=['POST'])
def logout():
    del session['user']
    return redirect("/blog")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = User.query.filter_by(email=email)
        if users.count() == 1:
            user = users.first()
            if password == user.password:
                session['user'] = user.email
                flash('welcome back, '+user.email)
                return redirect("/newpost")
            flash('User does not exist.')
            return redirect("/signup")
        flash('Incorrect password.')
        return redirect("/login")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        if not is_email(email):
            flash('zoiks! "' + email + '" does not seem like an email address')
            return redirect('/signup')
        email_db_count = User.query.filter_by(email=email).count()
        if email_db_count > 0:
            flash('yikes! "' + email + '" is already taken and password reminders are not implemented')
            return redirect('/signup')
        if password != verify:
            flash('passwords did not match')
            return redirect('/signup')
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        session['user'] = user.email
        return redirect("/")
    else:
        return render_template('signup.html')

def is_email(string):
    # for our purposes, an email string has an '@' followed by a '.'
    # there is an embedded language called 'regular expression' that would crunch this implementation down
    # to a one-liner, but we'll keep it simple:
    atsign_index = string.find('@')
    atsign_present = atsign_index >= 0
    if not atsign_present:
        return False
    else:
        domain_dot_index = string.find('.', atsign_index)
        domain_dot_present = domain_dot_index >= 0
        return domain_dot_present

@app.route('/blog', methods=['POST', 'GET'])
def read():
    blog_id = request.args.get('id')
    if (blog_id):
        blog = Blog.query.get(blog_id)
        return render_template('blogpost.html', blog=blog)


@app.route('/', methods=['GET', 'POST'])
def index():
    blogposts = Blog.query.all()
    return render_template('blog.html', blogposts=blogposts)

@app.route('/singleUser', methods=['GET', 'POST'])
def MyBlogs():
    blogposts = Blog.query.filter_by(owner_id=session['user']).first()
    return render_template('blog.html', blogposts=blogposts)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method == 'POST':
        new_title = request.form['title']
        new_content = request.form['content']
        title_error = ""
        content_error = ""
        if (not new_title) or (new_title.strip() == ""):
            title_error = "Please add a title to your blog post."
        if (not new_content) or (new_content.strip() == ""):
            content_error = "Please add some content to your blog post."
        if (title_error == "") and (content_error == ""):
            owner = User.query.filter_by(email=session['user']).first()
            new_blog = Blog(new_title, new_content, owner)
            db.session.add(new_blog)
            db.session.commit()
            link = './blog?id=' + str(new_blog.id)
            return redirect(link)
            #render_template('blogpost.html', title=new_title, body=new_content)
            #redirect('./blog?id={0}', id=new_blog.id, title=new_title, body=new_content)
        else:
            return render_template('newpost.html', 
            content_error=content_error, title_error=title_error, 
            new_content=new_content, new_title=new_title)
        
    else:
        return render_template('newpost.html')




if __name__ == '__main__':
    app.run()