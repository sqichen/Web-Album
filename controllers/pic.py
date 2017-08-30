from flask import *
from extensions import *
from config import *

pic = Blueprint('pic', __name__, template_folder='templates')

@pic.route('/pic', methods = ['GET', 'POST'])
def pic_route():

	db = connect_to_database()
	cur = db.cursor()
	picid = request.args.get('picid')

	cur.execute('SELECT picid FROM Photo WHERE picid=%s;', [picid])
	rows_count = cur.fetchall()
	if rows_count != 1:
		abort(404)

	#get pic format
	cur.execute('SELECT format FROM Photo WHERE picid=%s;', [picid])
	pformat = cur.fetchone()['format']

	#get albumid 
	cur.execute('SELECT albumid, sequencenum FROM Contain WHERE picid=%s;', [picid])
	photo = cur.fetchone()
	albumid = photo['albumid']
	sequencenum = photo['sequencenum']

	#prev_picid
	does_prev_pic_exist = False
	prev_picid = ""
	cur.execute('SELECT pic FROM Contain WHERE sequencenum<%s AND albumid=%s ORDER BY sequencenum DESC;', (sequencenum, albumid))
	row = cur.fetchone()
	if row is not None:
		does_prev_pic_exist = True
		prev_picid = row['picid']

	#next_picid
	does_next_pic_exist = False
	next_picid = ""
	cur.execute('SELECT pic FROM Contain WHERE sequencenum>%s AND albumid=%s ORDER BY sequencenum ASC;', (sequencenum, albumid))
	row = cur.fetchone()
	if row is not None:
		does_next_pic_exist = True
		next_picid = row['picid']


	return render_template("pic.html", albumid=albumid, picid=picid, pformat=pformat, 
							does_prev_pic_exist=does_prev_pic_exist, prev_picid=prev_picid,
							does_next_pic_exist=does_next_pic_exist, next_picid=next_picid)