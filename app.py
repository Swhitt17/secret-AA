from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User,Feedback
from forms import RegisterForm, LoginForm, DeleteForm, FeedbackForm
from werkzeug.exceptions import Unauthorized

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///secret_user"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "secrettunnel"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


context = app.app_context()
context.push()
connect_db(app)
db.create_all()


toolbar = DebugToolbarExtension(app)


@app.route('/')
def home_page():
    """Shows home page"""
    return redirect('/register')

@app.route('/register',methods=["GET","POST"] )
def register_user():
    """Shows form to register user"""

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        user = User.register(username,password,email,first_name,last_name)

        db.session.add(user)

        db.session.commit()
        session['username'] = user.username
        flash('Welcome! Your account has been created!', "success")
        return redirect(f'/users/{user.username}')
    else:
        return render_template("register.html", form=form)        
            


@app.route('/login', methods=["GET","POST"])
def login_user():
    """Shows form to login user"""
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username,password)
        if user:
            session["username"] = user.username
            flash(f"Welcome back, {user.username}!", "primary")
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ["Incorrect username/password"]
            return render_template("login.html", form=form)

    return render_template("login.html", form=form)


@app.route('/logout')
def logout_user():
    session.pop("username")
    flash("Goodbye!", "info")
    return redirect('/login')


        

@app.route('/users/<username>')
def show_user(username):
  """Returns page for logged in users """

  if "username" not in session or username != session['username']:
      raise Unauthorized()
  
  user = User.query.get(username)
  form = DeleteForm

  return render_template("details.html", user=user,form=form)


@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    """Deletes user and associated feedback"""
    if "username" not in session or username != session['username']:
        raise Unauthorized()
    
    user = User.query.get(username)
    db.session.delete(user)
    db.session.commit()
    session.pop("username")


@app.route('/users/<username>/feedback/add', methods = ["GET","POST"])
def add_feedback(username):
    """Shows and handles feedback form"""

    if "username" not in session or username != session['username']:
        raise Unauthorized()

    form = FeedbackForm()


    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        feedback = Feedback(title = title,
                            content = content,
                            username=username)
        
        db.session.add(feedback)
        db.session.commit()
        
        return redirect(f'/users/{feedback.username}')
    else:
           return render_template("create.html", form=form)
    

@app.route('/feedback/<feedback_id>/update', methods=["GET", "POST"])
def edit_feedback(feedback_id):
    """Shows and handles form for editing feedback"""

    feedback = Feedback.query.get(feedback_id)

    if "username" not in session or feedback.username != session['username']:
        raise Unauthorized()
    

    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f'/users/{feedback.username}')
    
    else:
        return render_template("edit.html", form=form, feedback=feedback)
    


@app.route('/feedback/<feedback_id>/delete', methods=["POST"])
def delete_feedback(feedback_id):
    """Delete feedback"""


    feedback = Feedback.query.get(feedback)

    if "username" not in session or feedback.username != session['username']:
        raise Unauthorized()
    
    form = DeleteForm
    
    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()

    return redirect(f'/users/{feedback.username}')
    


















