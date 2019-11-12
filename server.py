from flask import Flask, jsonify, request
import psycopg2
import json
import datetime

app = Flask(__name__,static_url_path="")
conn = psycopg2.connect("dbname=books user=postgres password=root")
#conn = psycopg2.connect("dbname=a3db user=a3user password=password")
CACHE = {}

@app.route('/')
def index():
	return open("index.html").read()


"""
format: 
result = [["year","word1", "word2"],
[2010, 3, 1],
[2012, 2, 1],
[2018, 4, 3],
[2019, 1, 1]]
"""	
@app.route('/data')
def data():
	#result = [["year","word1", "word2"],[2010, 3, 1],[2012, 2, 1],[2018, 4, 3],[2019, 1, 1]]
	#return jsonify(result)
	log = "17-1900," + str(datetime.datetime.now())

	global CACHE
	cur = conn.cursor()
	query_word = "SELECT distinct word FROM words WHERE length(word) = 17 ORDER BY word;"
	cur.execute(query_word)
	words = cur.fetchall()
	words = list(map(lambda x: x[0], words))
	header = ["year"] + words
	result = [header]

	query_year = "SELECT distinct year FROM words WHERE year < 1900 and year > 1850 ORDER BY year;"
	cur.execute(query_year)
	year = cur.fetchall()

	for y in year:
		query_each_year = "WITH q1 AS (SELECT OVERALL, word as w FROM words WHERE year = " + str(y[0])
		query_each_year += " and length(word)=17), q2 AS (SELECT distinct word FROM words WHERE length(word)=17) SELECT CASE WHEN OVERALL is NULL THEN 0 ELSE q1.overall END FROM q1 FULL OUTER JOIN q2 on q1.w = q2.word ORDER BY word;"
		cur.execute(query_each_year)
		count = cur.fetchall()
		count = list(map(lambda x:x[0],count))
		result.append([y[0]] + count)
		print(y)

	CACHE["25:1950"] = result
	cur.close()

	log += ","+str(datetime.datetime.now()) + "\n"	
	f = open("client.log","a")
	f.write(log)
	f.close()
	return jsonify(result)


@app.route('/other_len')
def other_len():
	l = request.args.get("l")
	y = request.args.get("y")
	log = str(l)+"-"+str(y) + "," + str(datetime.datetime.now())
	if l == "0" or y == "0":
		print("ALL")
		return all_data()
	#result = [["year","word2", "word3"],[2010, 3, 1],[2012, 2, 1],[2018, 4, 3],[2019, 1, 1]]
	#return jsonify(result)
	global CACHE
	cache_dict = l + ":" + y
	if cache_dict in CACHE:
		log += ","+str(datetime.datetime.now()) + "\n"
		f = open("client.log","a")
		f.write(log)
		f.close()
		return jsonify(CACHE[cache_dict])

	cur = conn.cursor()
	query_word = "SELECT distinct word FROM words WHERE length(word) = " + l + " ORDER BY word;"
	cur.execute(query_word)
	words = cur.fetchall()
	words = list(map(lambda x: x[0], words))
	header = ["year"] + words
	result = [header]

	query_year = "SELECT distinct year FROM words WHERE year > " + y + " AND year < " + str(int(y)+50) + " ORDER BY year;"
	cur.execute(query_year)
	year = cur.fetchall()
	for y in year:
		query_each_year = "WITH q1 AS (SELECT OVERALL, word as w FROM words WHERE year = " + str(y[0])
		query_each_year += " and length(word)=" + l + "), q2 AS (SELECT distinct word FROM words WHERE length(word)="+l+") SELECT CASE WHEN OVERALL is NULL THEN 0 ELSE q1.overall END FROM q1 FULL OUTER JOIN q2 on q1.w = q2.word ORDER BY word;"
		cur.execute(query_each_year)
		count = cur.fetchall()
		if count == []:
			tmp = [0]*len(words)
			tmp.insert(0,y[0])
			result.append([tmp])
		else:
			count = list(map(lambda x:x[0],count))
			result.append([y[0]] + count)


	CACHE[cache_dict] = result
	log += ","+str(datetime.datetime.now()) + "\n"
	f = open("client.log","a")
	f.write(log)
	f.close()
	cur.close()
	return jsonify(result)


# SELECT sum(OVERALL) FROM words WHERE year > 2000 and year < 2005
# "SELECT sum(OVERALL) FROM words WHERE year > " + str(year_start) + " and year < " + str(year_start+50) + ";"
def all_data():
	global CACHE
	f = open("client.log","a")
	log = "ALL," + str(datetime.datetime.now()) + ","

	year_start = 1500
	cache_dict = "0:0"
	if cache_dict in CACHE:	
		log += str(datetime.datetime.now()) + "\n"
		f.write(log)
		f.close()
		return jsonify(CACHE[cache_dict])

	header = ["year", "overall"] 
	result = [header]

	cur = conn.cursor()
	query_year = "SELECT distinct year FROM words WHERE year < 1900 and year > 1850 ORDER BY year;"
	cur.execute(query_year)
	year = cur.fetchall()

	for y in year: 
		query_year = "SELECT sum(OVERALL) FROM words WHERE year = " + str(y[0]) + ";"
		cur.execute(query_year)
		s = cur.fetchall()
		result.append([str(y[0]),s[0][0]])
	print(result)
	cur.close()
	log += str(datetime.datetime.now()) + "\n"
	f.write(log)
	f.close()
	return jsonify(result)







if __name__ == '__main__':
	f = open("client.log","w") 
	f.write("START," + str(datetime.datetime.now())+"\n")
	f.close()

	app.run(debug=True)
