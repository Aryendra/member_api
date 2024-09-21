from flask import Flask, render_template, g, request, json, jsonify
import sqlite3
from datetime import datetime
from functools import wraps

app = Flask(__name__)


app.config['DEBUG']=True


api_username='admin'
api_password='password'

def protected(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth=request.authorization
        if auth and auth.username== api_username and auth.password==api_password:
            return f(*args, **kwargs)
        
        else:
            return "access denied"
        
    return decorated
DATABASE = 'database.db'

# Function to get a connection to the SQLite database
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # Allows accessing columns by name
    return db

# Function to initialize the database with tables
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.executescript(f.read())  # Execute the SQL script
        db.commit()

# Route to confirm database creation


# Close the database connection after each request
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()



@app.route('/member' ,methods=['GET'])
@protected
def get_members():
    db=get_db()


    cur_member=db.execute('select id, name, email , level from members order by id desc')
    new_member=cur_member.fetchall()
    final_result=[]

    for one_member in new_member:
        d={}
        d['id']=one_member['id']
        d['name']=one_member['name']
        d['email']=one_member['email']
        d['level']=one_member['level']

        final_result.append(d)


   

   
        

    return jsonify({'members':final_result})
   




@app.route('/member/<int:member_id>' ,methods=['GET'])
@protected
def get_member(member_id):

    db=get_db()
    


    cur=db.execute('select id, name, email, level from members where id =(?)',[member_id])
    cur_result=cur.fetchone()
    return jsonify({"id":cur_result['id'],"name":cur_result['name'],"email":cur_result['email'],"level":cur_result['level']})



@app.route('/member' ,methods=['POST'])
@protected
def add_member():



    new_member_data= request.get_json()

    name=new_member_data['name']
    email=new_member_data['email']
    level=new_member_data['level']
    db=get_db()

    db.execute('insert into members (name, email, level) values (?,?,?)', [name,email,level])
    
    db.commit()

    cur_member=db.execute('select id, name, email , level from members where name = ?',[name])
    new_member=cur_member.fetchone()
    return jsonify({"id":new_member['id'], "name":new_member['name'], "email":new_member['email'], "level":new_member['level']})
    
    # return 'The name is {}, email is {}, level is {}'.format(name,email,level)


@app.route('/member/<int:member_id>' ,methods=['PUT','PATCH'])
@protected
def edit_member(member_id):
    new_member_data= request.get_json()

    name=new_member_data['name']
    email=new_member_data['email']
    level=new_member_data['level']
    db=get_db()

    db.execute('update  members set name=? where id= (?)', [name,member_id])
    
    db.commit()

    cur_member=db.execute('select id, name, email , level from members where id = ?',[member_id])
    updated_member=cur_member.fetchone()



    return jsonify({"id":updated_member['id'],"name":updated_member['name'],"email":updated_member['email'],"level":updated_member['level']})

@app.route('/member/<int:member_id>' ,methods=['DELETE'])
@protected
def delete_member(member_id):

    db=get_db()
    db.execute('delete from members where id =?',[member_id])
    db.commit()

    return 'row removed'


if __name__ == '__main__':
    app.run(debug=True)
