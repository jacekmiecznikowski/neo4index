from py2neo import Graph, Node, Relationship, authenticate
from passlib.hash import bcrypt
from urlparse import urlparse, urlunparse
from datetime import datetime
from dateutil import relativedelta
from statistics import median
import uuid, math
graphenedb_url = os.environ.get("GRAPHENEDB_BOLT_URL")
graphenedb_user = os.environ.get("GRAPHENEDB_BOLT_USER")
graphenedb_pass = os.environ.get("GRAPHENEDB_BOLT_PASSWORD")
graph = Graph(graphenedb_url, user=graphenedb_user, password=graphenedb_pass, bolt = True, secure = True, http_port = 24789, https_port = 24780)
#graph=Graph(user='neo4j', password='password')


class User:
	def __init__(self, username, firstname="", lastname=""):
		self.username = username
		self.firstname = firstname
		self.lastname = lastname

	def find(self):
		user = graph.find_one("User", "username", self.username)
		return user

	def register(self, password):
		if not self.find():
			user = Node("User", username=self.username, firstname=self.firstname, lastname=self.lastname, password=bcrypt.encrypt(password))
			graph.create(user)
			return True
		return False

	def verify_password(self, password):
		user = self.find()
		if not user:
			return False
		return bcrypt.verify(password, user["password"])

class Article:
	def __init__(self, article_id):
		self.article_id = article_id

	def get_article(self):
		query = """
		MATCH (article:Article)<-[:PUBLISHED]-(scientist:Scientist)
		WHERE article.id = {article_id}
		RETURN article.id, article.title, article.created, article.abstract, article.url, COLLECT({id:id(scientist),data:scientist}) AS scientists
		"""
		return graph.run(query, article_id=self.article_id).data()[0]

	def get_out_citations(self):
		query= """
		MATCH (article:Article)
		WHERE article.id = {article_id}
		WITH article
		MATCH (article)-[:CITES]->(publication:Article)
		RETURN COLLECT(publication) AS data	
		"""
		return graph.run(query, article_id=self.article_id).data()[0]

	def get_in_citations(self):
		query= """
		MATCH (article:Article)
		WHERE article.id = {article_id}
		WITH article
		MATCH (article)<-[:CITES]-(publication:Article)
		RETURN COLLECT(publication) AS data	
		"""
		return graph.run(query, article_id=self.article_id).data()[0]

	def get_categories(self):
		query= """
		MATCH (article:Article)
		WHERE article.id = {article_id}
		WITH article
		MATCH (article)-[:WITHIN]->(category:Category)
		RETURN COLLECT(category) AS data	
		"""
		return graph.run(query, article_id=self.article_id).data()[0]

class Scientist:
	def __init__(self, scientist_id):
		self.scientist_id = scientist_id

	def get_data(self):
		query = """
		MATCH (scientist:Scientist)
		WHERE ID(scientist) = {scientist_id}
		RETURN ID(scientist) as id, scientist.first_name as first_name, scientist.last_name as last_name
		"""
		return graph.run(query, scientist_id=self.scientist_id).data()[0]

	def get_articles(self):
		query = """
		MATCH (scientist:Scientist)-[:PUBLISHED]->(article:Article)
		WHERE ID(scientist) = {scientist_id}
		RETURN collect(article) as data
		"""
		return graph.run(query, scientist_id=self.scientist_id).data()[0]

def get_articles(n, page):
	query = """
	MATCH (article:Article) RETURN article.id as id, article.title as title, article.created as created SKIP ({page}-1) * {n} LIMIT {n}
	"""
	return graph.run(query, n=n, page=page).data()

def get_articles_count():
	query = """
	MATCH(article:Article) RETURN count(*) as num
	"""
	return graph.run(query).data()[0].get("num")

def get_scientists(n, page):
	query = """
	MATCH (scientist:Scientist) RETURN ID(scientist) as id, scientist.first_name as first_name, scientist.last_name as last_name SKIP ({page}-1) * {n} LIMIT {n}
	"""
	return graph.run(query, n=n, page=page).data()

def get_all_scientists():
	query = """
	MATCH (scientist:Scientist) RETURN ID(scientist) as id, scientist.first_name as first_name, scientist.last_name as last_name
	"""
	return graph.run(query)

def get_scientists_count():
	query = """
	MATCH(scientist:Scientist) RETURN count(*) as num
	"""
	return graph.run(query).data()[0].get("num")

	
def h_index(scientist_id):
	scientist_id = int(scientist_id)
	query = """
	MATCH (scientist:Scientist) WHERE ID(scientist) = {scientist_id}
	WITH scientist
	MATCH (scientist)-[:PUBLISHED]->(article:Article)
	with article
	MATCH (article)<-[citing:CITES]-(:Article)
	WITH article, COUNT(citing) as citation
    RETURN citation ORDER BY citation ASC
	"""
	result = graph.run(query, scientist_id=scientist_id).data()
	citations = [x['citation'] for x in result]
	n = len(citations)
	l, r = 0, n-1
	while l <= r:
		mid = (l+r)//2
		if citations[mid] >= n-mid:
			r = mid - 1
		else:
			l = mid + 1
	return n-l

def m_quotient(scientist_id):
	scientist_id = int(scientist_id)
	query = """
	MATCH (scientist:Scientist) WHERE ID(scientist) = {scientist_id}
	WITH scientist
	MATCH (scientist)-[:PUBLISHED]->(article:Article)
	with article
	MATCH (article)<-[citing:CITES]-(:Article)
	WITH article, COUNT(citing) as citation
    RETURN citation ORDER BY citation ASC
	"""
	result = graph.run(query, scientist_id=scientist_id).data()
	citations = [x['citation'] for x in result]
	n = len(citations)
	l, r = 0, n-1
	while l <= r:
		mid = (l+r)//2
		if citations[mid] >= n-mid:
			r = mid - 1
		else:
			l = mid + 1
	query = """
	MATCH (scientist:Scientist)-[:PUBLISHED]->(article:Article)
	WHERE ID(scientist) = {scientist_id}
	RETURN article['created'] as created ORDER BY created ASC LIMIT 1
	"""
	result = graph.run(query, scientist_id=scientist_id).data()[0].get('created')
	first = datetime.strptime(result, '%Y-%m-%d')
	now = datetime.now()
	y = relativedelta.relativedelta(now, first).years
	if y == 0:
		y = 1
	return round((n-l)/y,4)

def e_index(scientist_id):
	scientist_id = int(scientist_id)
	query = """
	MATCH (scientist:Scientist) WHERE ID(scientist) = {scientist_id}
	WITH scientist
	MATCH (scientist)-[:PUBLISHED]->(article:Article)
	with article
	MATCH (article)<-[citing:CITES]-(:Article)
	WITH article, COUNT(citing) as citation
    RETURN citation ORDER BY citation ASC
	"""
	result = graph.run(query, scientist_id=scientist_id).data()
	citations = [x['citation'] for x in result]
	n = len(citations)
	l, r = 0, n-1
	while l <= r:
		mid = (l+r)//2
		if citations[mid] >= n-mid:
			r = mid - 1
		else:
			l = mid + 1
	hindex = n-l
	hcore = citations[-hindex:]
	e = math.sqrt(sum(hcore) - math.pow(hindex,2))
	return round(e,4)

def m_index(scientist_id):
	scientist_id = int(scientist_id)
	query = """
	MATCH (scientist:Scientist) WHERE ID(scientist) = {scientist_id}
	WITH scientist
	MATCH (scientist)-[:PUBLISHED]->(article:Article)
	with article
	MATCH (article)<-[citing:CITES]-(:Article)
	WITH article, COUNT(citing) as citation
    RETURN citation ORDER BY citation ASC
	"""
	result = graph.run(query, scientist_id=scientist_id).data()
	citations = [x['citation'] for x in result]
	n = len(citations)
	l, r = 0, n-1
	while l <= r:
		mid = (l+r)//2
		if citations[mid] >= n-mid:
			r = mid - 1
		else:
			l = mid + 1
	hindex = n-l
	hcore = citations[-hindex:]
	if hcore:
		m = median(hcore)
	else:
		m = 0
	return round(m,4)

def r_index(scientist_id):
	scientist_id = int(scientist_id)
	query = """
	MATCH (scientist:Scientist) WHERE ID(scientist) = {scientist_id}
	WITH scientist
	MATCH (scientist)-[:PUBLISHED]->(article:Article)
	with article
	MATCH (article)<-[citing:CITES]-(:Article)
	WITH article, COUNT(citing) as citation
    RETURN citation ORDER BY citation ASC
	"""
	result = graph.run(query, scientist_id=scientist_id).data()
	citations = [x['citation'] for x in result]
	n = len(citations)
	l, r = 0, n-1
	while l <= r:
		mid = (l+r)//2
		if citations[mid] >= n-mid:
			r = mid - 1
		else:
			l = mid + 1
	hindex = n-l
	hcore = citations[-hindex:]
	rindex = math.sqrt(sum(hcore))

	return round(rindex,4)

def ar_index(scientist_id):
	scientist_id = int(scientist_id)
	query = """
	MATCH (scientist:Scientist) WHERE ID(scientist) = {scientist_id}
	WITH scientist
	MATCH (scientist)-[:PUBLISHED]->(article:Article)
	with article
	MATCH (article)<-[citing:CITES]-(:Article)
	WITH article, COUNT(citing) as citation
    RETURN article.created as date, citation ORDER BY citation ASC
	"""
	result = graph.run(query, scientist_id=scientist_id).data()
	citations = [x['citation'] for x in result]
	dates = [relativedelta.relativedelta(datetime.now(), datetime.strptime(x['date'], '%Y-%m-%d')).years for x in result]
	dates = [x if x > 0 else 1 for x in dates]
	n = len(citations)
	l, r = 0, n-1
	while l <= r:
		mid = (l+r)//2	
		if citations[mid] >= n-mid:
			r = mid - 1
		else:
			l = mid + 1
	hindex = n-l
	hcore = citations[-hindex:]
	hdates = dates[-hindex:]	
	arindex = [x / y for x, y in zip(hcore, hdates)]
	arindex = math.sqrt(sum(arindex))

	return round(arindex,4)