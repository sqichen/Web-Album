from flask import *
from extensions import *
from config import *
import os
import hashlib
import time

album = Blueprint('album', __name__, template_folder='templates')

IMAGE_FOLDER_PREFIX = 'static/images'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'bmp', 'gif'])

def generate_picid(filename, albumid):
	picid = hashlib.md5()
	picid.update(str(albumid).encode('utf-8'))
	picid.update(filename.encode('utf-8'))
	return picid.hexdigest()

def display_photos(cur, albumid):
	db = connect_to_database()
	cur = db.cursor()
	cur.execute('SELECT sequencenum, picid FROM Contain WHERE albumid=%s;', [albumid])
	photos = cur.fetchall()
	picid_format_sequencenum_tuples = []
	for photo in photos:
		picid = photo['picid']
		cur.execute('SELECT format FROM Photo WHERE picid=%s;', [picid])
		pformat = cur.fetchone()['format']
		sequencenum = photo['sequencenum']
		picid_format_sequencenum_tuple = (picid, pformat, sequencenum)
		picid_format_sequencenum_tuples.append(picid_format_sequencenum_tuple)

	sorted(picid_format_sequencenum_tuples, key=lambda instance: instance[2])
	return picid_format_sequencenum_tuples


@album.route('/album/edit', methods=['GET', 'POST'])
def album_edit_route():
	albumid = request.args.get('albumid')
	if albumid is None: 
		abort(404)
	db = connect_to_database()
	cur = db.cursor()
	cur.execute('SELECT albumid FROM Album WHERE albumid=%s;', [albumid])
	number_of_records = cur.rowcount
	if number_of_records != 1:
		abort(404)

	now = time.strftime('%Y-%m-%d', time.localtime(time.time()))

	op = request.form.get('op')
	if op == "add":
		f = request.file['file']
		if f.filename != '':
			filename_extension = f.filename[-3:].lower()
			if filename_extension in ALLOWED_EXTENSIONS:
				picid = generate_picid(f.filename, albumid)

				f.save(os.path.join(IMAGE_FOLDER_PREFIX, picid + '.' + filename_extension))

				try:
					cur.execute('INSERT INTO Photo (picid, format, date) VALUES (%s, %s, %s);', (picid, filename_extension, now))

				except:
					print(cur._last_executed)
					abort(404)

				cur.execute('SELECT sequencenum FROM Contain;')	

				existing_sequencenums = cur.fetchall()
				new_sequencenum = -1
				for existing_sequencenum in existing_sequencenums:
					if new_sequencenum < existing_sequencenum['sequencenum']:
						new_sequencenum = existing_sequencenum['sequencenum']
				new_sequencenum += 1		

				try: 
					cur.execute('INSERT INTO Contain (sequencenum, albumid, picid, caption) VALUES (%s, %s, %s, '');', (new_sequencenum, albumid, picid))
				except:
					print(cur._last_executed)
					abort(404)

				cur.execute('UPDATE Album SET lastupdated=%s WHERE albumid=%s;', (now, albumid))

	elif op = "delete":
		picid = request.form.get('picid')

		cur.execute('SELECT COUNT(sequencenum) FROM Contain WHERE albumid=%s AND picid=%s;', (albumid, picid))
		number_of_records = cur.rowcount
		if number_of_records != 1:
			abort(404)

		#1. delete from Photo
		cur.execute('SELECT format FROM Photo WHERE picid=%s;', [picid])
		pformat = cur.fetchone()['format']
		cur.execute('DELETE FROM Photo WHERE picid=%s;', [picid])

		#2. delete from Contain
		cur.execute('DELETE FROM Contain WHERE albumid=%s AND picid=%s;', (albumid, picid))

		#3. delete from desk
		os.remove(os.path.join(IMAGE_FOLDER_PREFIX, picid + '.' + pformat))

		#4. update Album lastupdated
		cur.execute('UPDATE Album SET lastupdated=%s WHERE albumid=%s;', (now, albumid))

	picid_format_sequencenum_tuples = display_photos(cur, albumid)

	cur.execute('SELECT title FROM Album WHERE albumid=%s;', [albumid])
	title = cur.fetchone()

	options = {
		"edit": True
	}
	return render_template("album.html", picid_format_sequencenum_tuples=picid_format_sequencenum_tuples, title=title, albumid=albumid, **options)

@album.route('/album', methods=['POST', 'GET'])
def album_route():
	albumid = request.args.get('albumid')
	if albumid is None:
		abort(404)

	db = connect_to_database()
	cur = db.cursor()

	cur.execute('SELECT albumid FROM Album WHERE albumid=%s;', [albumid])
	number_of_records = cur.rowcount
	if number_of_records != 1:
		abort(404)

	picid_format_sequencenum_tuples = display_photos(cur, albumid)

	cur.execute('SELECT title FROM Album WHERE albumid=%s;', [albumid])
	title=cur.fetchone()

	options = {
		"edit": False
	}
	return render_template("album.html", picid_format_sequencenum_tuples=picid_format_sequencenum_tuples, title=title, albumid=albumid, **options)
