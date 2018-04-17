from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blogger@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

#Classes---------------------------------------------------------------
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300))
    body = db.Column(db.String(5000))

    def __init__(self, title, body):
        self.title = title
        self.body = body


#Handlers------------------------------------------------------------
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
            new_blog = Blog(new_title, new_content)
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