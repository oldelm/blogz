from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:cheese@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, owner):
        self.title = title
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['show_login', 'login', 'signup', 'show_signup', 'show_blogs', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')




#@app.route('/', methods=['POST', 'GET'])
#def index():
#    return redirect('/blog')

@app.route('/', methods=['POST', 'GET'])
def index():
    allusers = User.query.all()
    # >>> x
    #[1, 2, 3, 0, 4, 0, 5]
    #>>> foo = [num for num in x if num != 0]
    #>>> foo
    #[1, 2, 3, 4, 5]
    #using list comprehensions:
    # so: to get all the ones with blogs (I hope):
    allauthors = [u for u in allusers if u.blogs]    
    return render_template('index.html', authors=allauthors)

# shows blog posts:
@app.route('/blog', methods=['GET'])
def show_blogs():
    if request.args.get('id'):
        myid = request.args.get('id')
        #print("myid:", myid)
        myblog = Blog.query.filter_by(id=myid).all()
        #print("myblog:", myblog)
        return render_template('new.html', blog=myblog[0])
    
    # get the userid, and then use it to get the user from the db
    if request.args.get('user'):
        myuserid = request.args.get('user')
        #myuser = User.query.filter_by(id=myuserid).all().first()
        myuser = User.query.filter_by(id=myuserid).first()
        return render_template('singleUser.html', user=myuser)
    
    bloglist = Blog.query.all()
    #print("bloglist:", bloglist)
    
    return render_template('blog-list.html', blogs=bloglist, title="Build A Blog")



@app.route('/newpost')
def new_form():
    return render_template('add-post.html')

@app.route('/newpost', methods=['POST'])
def add_new():
    mytitle = request.form['title']
    mybody = request.form['body']
    title_err = ''
    body_err = ''
    # myuser = User.query.filter_by(username=session['username']).first()
    
    # no title, no body results in error: 
    if not mytitle:
        title_err = 'Please fill in the title'
    if not mybody:
        body_err = 'Please fill in the body'
    
    # entering only blank spaces results in error:
    if mytitle.isspace():
        title_err = 'Please fill in the title'
    if mybody.isspace():
        body_err = 'Please fill in the body'
    
    if not title_err and not body_err:
        myowner = User.query.filter_by(username=session['username']).first()
        myblog = Blog(mytitle, myowner)
        myblog.body = mybody
        db.session.add(myblog)
        db.session.commit()
        newurl = '/blog?id=' + str(myblog.id)
        return redirect(newurl)
    else:
        return render_template('add-post.html', title=mytitle , titleblank=title_err , body=mybody , bodyblank=body_err)


@app.route('/login')
def show_login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    myusername = request.form['username']
    mypassword = request.form['password']
    username_err = ''
    password_err = ''

    # no username results in error: 
    if not myusername:
        username_err = 'Please fill in the username'

    # incorrect username results in error:
    user = User.query.filter_by(username=myusername).first()
    if myusername and not user:
        username_err = 'That is not the name of a registered user'

    # no password results in error: 
    if not mypassword:
        password_err = 'Please fill in the password'
    
    # entering only blank spaces results in error:
    if myusername.isspace():
        username_err = 'Please fill in the username'
    if mypassword.isspace():
        password_err = 'Please fill in the password'
    
    # if no errors then create session and redirect to /newpost
    if not username_err and not password_err:
        if user.password == mypassword:
            session['username'] = myusername
            # flash("Logged in")
            return redirect('/newpost')
        
        # correct username incorrect password results in error:
        else:
            password_err = 'That password is incorrect'
            
    
    return render_template('login.html', username=myusername , usernameerror=username_err , password=mypassword , passworderror=password_err)


@app.route('/signup')
def show_signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup():
    myusername = request.form['username']
    print("myusername: ", myusername)
    mypassword = request.form['password']
    myverify = request.form['verify']
    username_err = ''
    password_err = ''
    verify_err = ''

    # no username, no password, no verify results in error: 
    if not myusername:
        username_err = 'Please fill in the username'
    if not mypassword:
        password_err = 'Please fill in the password'
    if not myverify:
        verify_err = 'Please fill in the password verification'
    
    # entering only blank spaces results in error:
    if myusername.isspace():
        username_err = 'Please fill in the username'
    if mypassword.isspace():
        password_err = 'Please fill in the password'
    if myverify.isspace():
        password_err = 'Please fill in the password verification'
    
    # password and verrify password not matching results in error:
    if mypassword != myverify:
        verify_err = 'Passwords do not match'

    # if username is less than 3 characters long there's an error:
    if len(myusername) < 3:
        username_err = 'Please enter a longer username'
    
    # if password is less than 3 characters long there's an error:
    if len(mypassword) < 3:
        password_err = 'Please enter a longer password'

    # if username already exists in database there's an error:
    if myusername:
        existing_user = User.query.filter_by(username=myusername).first()
        if existing_user: 
            username_err = 'Looks like that user already exists'
    # ^could make that more efficient with the existing_user assignment 
    # but i'm worried about screwing up the next conditional, which works just fine
    # ^ i can remove it if it causes problems

    if not username_err and not password_err and not verify_err:
        existing_user = User.query.filter_by(username=myusername).first()
        if not existing_user:
            new_user = User(myusername, mypassword)
            print("myusername: ", myusername)
            print("new_user.username:", new_user.username)
            db.session.add(new_user)
            db.session.commit()
            print("myusername: ", myusername)
            print("new_user.username:", new_user.username)
            session['username'] = myusername
            return redirect('/newpost')
            print("myusername: ", myusername)
            print("new_user.username:", new_user.username)
        else:
            # TODO - user better response messaging
            #return "<h1>Duplicate user</h1>"
            username_err = 'Looks like that user already exists'

    return render_template('signup.html', verify=myverify, verifypassworderror=verify_err, username=myusername , usernameerror=username_err , password=mypassword , passworderror=password_err)


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


if __name__ == '__main__':
    app.run()