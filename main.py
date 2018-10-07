from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:cheese@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    deleted = db.Column(db.Boolean)

    def __init__(self, title):
        self.title = title
        self.deleted = False


@app.route('/', methods=['POST', 'GET'])
def index():
    return redirect('/blog')
    

    
@app.route('/blog', methods=['GET'])
def show_blogs():
    #show just one blog entry
    if request.args.get('id'):
        myid = request.args.get('id')
        print("myid:", myid)
        myblog = Blog.query.filter_by(id=myid).all()
        print("myblog:", myblog)
        return render_template('new.html', blog=myblog[0])
    
    #blogs = Blog.query.filter_by(deleted=False).all()
    bloglist = Blog.query.all()
    print("bloglist:", bloglist)
    #deleted_blogs = Blog.query.filter_by(deleted=True).all()
    
    
    return render_template('blog-list.html', blogs=bloglist, title="Build A Blog")


#maybe could use this to delte blog posts in the future:

#@app.route('/delete-task', methods=['POST'])
#def delete_task():

#    blog_id = int(request.form['blog-id'])
#    blog = Task.query.get(blog_id)
#    blog.deleted = True
#    db.session.add(blog)
#    db.session.commit()

#    return redirect('/')

@app.route('/newpost')
def new_form():
    return render_template('add-post.html')

@app.route('/newpost', methods=['POST'])
def add_new():
    mytitle = request.form['title']
    mybody = request.form['body']
    title_err = ''
    body_err = ''
    
    #no title, no body results in error: 
    if not mytitle:
        title_err = 'Please fill in the title'
    if not mybody:
        body_err = 'Please fill in the body'
    
    #entering only blank spaces results in error:
    if mytitle.isspace():
        title_err = 'Please fill in the title'
    if mybody.isspace():
        body_err = 'Please fill in the body'
    
    if not title_err and not body_err:
        myblog = Blog(mytitle)
        myblog.body = mybody
        db.session.add(myblog)
        db.session.commit()
        newurl = '/blog?id=' + str(myblog.id)
        return redirect(newurl)
    else:
        return render_template('add-post.html', title=mytitle , titleblank=title_err , body=mybody , bodyblank=body_err)


if __name__ == '__main__':
    app.run()