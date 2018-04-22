from flask import request, redirect, render_template, session, flash
from models import Blog, User
from app import app, db

endpoints_without_login = ['login', 'signup']

#Handlers------------------------------------------------------------

#@app.before_request
def require_login():
    if not ('user' in session or request.endpoint in endpoints_without_login):
        flash("Please login.")
        return redirect("/login")

@app.route("/logout", methods=['POST', 'GET'])
def logout():
    del session['user']
    return redirect("/login")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = User.query.filter_by(email=email)
        if (password.strip() == "") and (email.strip() == ""):
            flash("Please login.")
            return redirect("/login")
        if users.count() == 1:
            user = users.first()
            if password == user.password:
                session['user'] = user.email
                flash('welcome back, '+user.email)
                return redirect("/newpost")
            if password != user.password:
                flash('Incorrect password.')
                return render_template("login.html", email=email)
        else:
            flash('User does not exist.')
            return redirect("/signup")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        if not is_email(email):
            flash('zoiks! ' + email + ' does not seem like an email address')
            return redirect('/signup')
        email_db_count = User.query.filter_by(email=email).count()
        if email_db_count > 0:
            flash('yikes! "' + email + '" is already taken and password reminders are not implemented')
            return redirect('/signup')
        if password != verify:
            flash('passwords did not match')
            return render_template("signup.html", email=email)
        user = User(email, password)
        db.session.add(user)
        db.session.commit()
        session['user'] = user.email
        flash("Welcome to the blog," + email + "!")
        return redirect("/")
    
    return render_template('signup.html')

def is_email(email):
    count_at = 0
    count_period = 0
    count_space = 0
    count_email = 0
    for i in email:
        count_email = count_email + 1
        if i == "@":
            count_at = count_at + 1
        else:
            count_at = count_at
        if i == ".":
            count_period = count_period + 1
        else:
            count_period = count_period
        if i == " ":
            count_space = count_space + 1
        else:
            count_space = count_space
    if (count_period < 1) or (count_at != 1) or (count_space > 0) or (count_email > 30 or count_email < 3):
        return False
    else:
        return True

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
    if not ('user' in session or request.endpoint in endpoints_without_login):
        flash("Please login.")
        return redirect("/login")
    else:
        owner = User.query.filter_by(email=session['user']).first()
        blogposts = Blog.query.filter_by(owner=owner).all()
        return render_template('singleUser.html', blogposts=blogposts)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if not ('user' in session or request.endpoint in endpoints_without_login):
        flash("Please login.")
        return redirect("/login")
    if request.method == 'POST':
        new_title = request.form['title']
        new_content = request.form['content']
        if (not new_title) or (new_title.strip() == ""):
            flash("Please add a title to your blogpost.")
        if (not new_content) or (new_content.strip() == ""):
            flash("Please add content to your blogpost.")
        elif (new_title or new_title.strip() != "") and (new_content or new_content.strip() != ""):
            owner = User.query.filter_by(email=session['user']).first()
            new_blog = Blog(new_title, new_content, owner)
            db.session.add(new_blog)
            db.session.commit()
            link = './blog?id=' + str(new_blog.id)
            return redirect(link)
            #render_template('blogpost.html', title=new_title, body=new_content)
            #redirect('./blog?id={0}', id=new_blog.id, title=new_title, body=new_content)
        return render_template('newpost.html', 
        new_content=new_content, new_title=new_title)
        
    else:
        return render_template('newpost.html')




if __name__ == '__main__':
    app.run()