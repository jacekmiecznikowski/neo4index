from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify, abort
from .models import *
from .forms import SignupForm, LoginForm
from timeit import default_timer as timer
from math import ceil
import csv
app = Flask (__name__)

@app.route('/')
def index():
	return render_template('home.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/about')
def about():
	data = {}
	data['articles'] = get_articles_count()
	data['scientists'] = get_scientists_count()
	return render_template('about.html', data=data)

@app.route("/register", methods=["GET", "POST"])
def register():
	if "username" in session:
		return redirect(url_for("index"))
	form = SignupForm()
	if request.method == "POST":
		user = User(request.form["username"], request.form["first_name"], request.form["last_name"])
		if form.validate() == False:
			return render_template("register.html", form=form)
		if not user.register(request.form["password"]):
			flash("User with this username already exists.")
		else:
			flash("You have successfully registered!")
			return redirect(url_for("index"))
	return render_template("register.html", form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
	if "username" in session:
		return redirect(url_for("index"))
	form = LoginForm()
	if request.method == "POST":
		if form.validate() == False:
			return render_template("login.html", form=form)
		user = User(request.form["username"])
		if not user.verify_password(request.form["password"]):
			flash("Incorrect username or password.")
		else:
			flash("Logged in!")
			session["username"] = user.username
			return redirect(url_for("index"))
	return render_template("login.html", form=form)

@app.route("/logout")
def logout():
	if "username" in session:
		session.pop("username")
		flash("Logged out.")
	return redirect(url_for("index"))

@app.route('/articles')
def articles():
	if "username" not in session:
		return redirect(url_for("login"))
	page = request.args.get('page', default=1, type=int)
	perpage = 30
	pages_count = ceil(get_articles_count()/perpage)
	articles = get_articles(perpage, page)
	return render_template('articles.html', articles=articles, page=page, pages_count=pages_count)

@app.route('/articles/<int:article_id>')
def article(article_id):
	if "username" not in session:
		return redirect(url_for("login"))
	article = Article(article_id)
	data = article.get_article()
	categories = article.get_categories()
	outgoing = article.get_out_citations()
	ingoing = article.get_in_citations()
	return render_template('article.html', article=data, outgoing=outgoing, ingoing=ingoing, categories=categories)

@app.route('/scientists')
def scientists():
	if "username" not in session:
		return redirect(url_for("login"))
	page = request.args.get('page', default=1, type=int)
	perpage = 30
	pages_count = ceil(get_scientists_count()/perpage)
	scientists = get_scientists(perpage, page)
	return render_template('scientists.html', scientists=scientists, page=page, pages_count=pages_count)

@app.route('/scientists/<int:scientist_id>')
def scientist(scientist_id):
	if "username" not in session:
		return redirect(url_for("login"))
	scientist = Scientist(scientist_id)
	data = scientist.get_data()
	articles = scientist.get_articles()
	return render_template('scientist.html', scientist=data, articles=articles)

@app.route('/db')
def db():
	if "username" not in session:
		return redirect(url_for("login"))
	return render_template('db.html')

@app.route('/_hindex')
def hindex():
	if "username" not in session:
		return redirect(url_for("login"))
	try:
		start = timer()
		scientist_id = request.args.get('id')
		result = h_index(scientist_id)
		end = timer()
		elapsed_time = round(end - start,6)
		return jsonify(result=result, elapsed_time=elapsed_time)
	except:
		abort(404)

@app.route('/_mquotient')
def mquotient():
	if "username" not in session:
		return redirect(url_for("login"))
	try:
		start = timer()
		scientist_id = request.args.get('id')
		result = m_quotient(scientist_id)
		end = timer()
		elapsed_time = round(end - start,6)
		return jsonify(result=result, elapsed_time=elapsed_time)
	except:
		abort(404)

@app.route('/_eindex')
def eindex():
	if "username" not in session:
		return redirect(url_for("login"))
	try:
		start = timer()
		scientist_id = request.args.get('id')
		result = e_index(scientist_id)
		end = timer()
		elapsed_time = round(end - start,6)
		return jsonify(result=result, elapsed_time=elapsed_time)
	except:
		abort(404)

@app.route('/_mindex')
def mindex():
	if "username" not in session:
		return redirect(url_for("login"))
	try:
		start = timer()
		scientist_id = request.args.get('id')
		result = m_index(scientist_id)
		end = timer()
		elapsed_time = round(end - start,6)
		return jsonify(result=result, elapsed_time=elapsed_time)
	except:
		abort(404)

@app.route('/_rindex')
def rindex():
	if "username" not in session:
		return redirect(url_for("login"))
	try:
		start = timer()
		scientist_id = request.args.get('id')
		result = r_index(scientist_id)
		end = timer()
		elapsed_time = round(end - start,6)
		return jsonify(result=result, elapsed_time=elapsed_time)
	except:
		abort(404)

@app.route('/_arindex')
def arindex():
	if "username" not in session:
		return redirect(url_for("login"))
	try:
		start = timer()
		scientist_id = request.args.get('id')
		result = ar_index(scientist_id)
		end = timer()
		elapsed_time = round(end - start,6)
		return jsonify(result=result, elapsed_time=elapsed_time)
	except:
		abort(404)

@app.route('/_bulk')
def bulk():
	if "username" not in session:
		return redirect(url_for("login"))
	method = request.args.get('method')
	save = request.args.get('csv')
	if method == 'all':
		if save == 'true':
			with open('app/static/download/all.csv', 'w') as outcsv:
				writer = csv.writer(outcsv, delimiter=',')
				writer.writerow(["id", "first_name", "last_name", "h-index", "m quotient", "e-index", "m-index", "r-index", "ar-index"])				
				start = timer()
				cursor = get_all_scientists()
				for record in cursor:
					hindex = h_index(record['id'])
					mquotient = m_quotient(record['id'])
					eindex = e_index(record['id'])
					mindex = m_index(record['id'])
					rindex = r_index(record['id'])
					arindex = ar_index(record['id'])
					writer.writerow([record['id'],record['first_name'],record['last_name'],hindex,mquotient,eindex,mindex,rindex,arindex])
				end = timer()
				elapsed_time = round(end - start,6)
				return jsonify(elapsed_time=elapsed_time)
		elif save == 'false':
			start = timer()
			cursor = get_all_scientists()
			for record in cursor:
				hindex = h_index(record['id'])
				mquotient = m_quotient(record['id'])
				eindex = e_index(record['id'])
				mindex = m_index(record['id'])
				rindex = r_index(record['id'])
				arindex = ar_index(record['id'])
			end = timer()
			elapsed_time = round(end - start,6)
			return jsonify(elapsed_time=elapsed_time)

	elif method in ('h_index', 'm_quotient', 'e_index', 'm_index', 'r_index', 'ar_index'):
		if save == 'true':
			with open('app/static/download/'+method+'.csv', 'w') as outcsv:
				writer = csv.writer(outcsv, delimiter=',')
				writer.writerow(["id", "first_name", "last_name", method])			
				start = timer()
				cursor = get_all_scientists()
				result = 0
				for record in cursor:
					result = eval(method + '('+str(record['id'])+')')
					writer.writerow([record['id'],record['first_name'],record['last_name'],result])
				end = timer()
				elapsed_time = round(end - start,6)
				return jsonify(elapsed_time=elapsed_time)
		elif save == 'false':
			start = timer()
			cursor = get_all_scientists()
			for record in cursor:
				result = eval(method + '('+str(record['id'])+')')
			end = timer()
			elapsed_time = round(end - start,6)
			return jsonify(elapsed_time=elapsed_time)
	else:
		abort(404)