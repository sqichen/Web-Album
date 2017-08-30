from flask import *
import os
import time
from extensions import connect_to_database

albums = Blueprint('albums', __name__, template_folder='templates')

IMAGE_FOLDER_PREFIX = '/static/images'

@albums.route('/albums/edit', methods = ['GET','POST'])
def albums_edit_route():
	username = request.args.get('username')
	db = connect_to_database()
	cur = db.cursor()
	row_count = cur.execute("SELECT * FROM User WHERE username = %s;", [username])
	if row_count == 0:
		abort(404)

	op=request.form.get('op')

	if op == "delete":
		albumid = request.form.get('albumid')

		#1. delete in Contain
		cur.execute('SELECT picid FROM Contain WHERE albumid=%s;', [albumid])
		picid_to_remove = cur.fetchall()
		cur.execute('DELETE FROM Contain WHERE albumid=%s;', [albumid])

		for picid in picid_to_remove:
			#2. delete in Photo
			pformat = cur.execute('SELECT format FROM Photo WHERE picid=%s;', [picid])
			cur.execute('DELETE picid FROM Photo WHERE picid=%s;', [picid])

			#3. delete in images
			os.remove(IMAGE_FOLDER_PREFIX + picid + '.' + pformat)

		#4. delete in Album
		cur.execute('DELETE FROM Album WHERE albumid=%s;', [albumid])

	elif op == "add":
		title = request.form.get("title")
		now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
		cur.execute('INSERT into Album (title, created, lastupdated, username) VALUES (%s, %s, %s, %s);', (title, now, now, username))

	cur.execute('SELECT albumid, title FROM Album WHERE username=%s;', [username])
	all_albums=cur.fetchall()


	options = {
		"edit": True
	}
	return render_template("albums.html", username=username, albums=all_albums, **options)


@albums.route('/albums')
def albums_route():
	username = request.args.get('username')
	db = connect_to_database()
	cur = db.cursor()
	row_count = cur.execute('SELECT * FROM User WHERE username=%s;', [username])
	if row_count == 0:
		abort(404)
	cur.execute('SELECT albumid, title FROM Album WHERE username=%s;', [username])
	all_albums = cur.fetchall()
	options = {
		"edit": False
	}
	return render_template("albums.html", albums=all_albums, username=username, **options)