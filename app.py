from flask import *
import pymysql
import mpesa
from functions import *
# from werkzeug.utils import secure_filename
# import os


app = Flask(__name__)
app.secret_key = "dkdinmartparcfddwedgf"

# UPLOAD_FOLDER = 'images'

# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)

#     ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

#     # function to check if file extension is allowed
#     def allowed_file(filename):
#         return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    connection = pymysql.connect(host='localhost', user='root', password='', database='nekesa_rental')
    cursor = connection.cursor()
    sql1 = "select * from house_details where house_type = %s"
    cursor.execute(sql1, "singles")
    singles = cursor.fetchall()

    sql2 = "select * from house_details where house_type = %s"
    cursor.execute(sql2, "bedsitters")
    bedsitters = cursor.fetchall()

    sql3 = "select * from house_details where house_type = %s"
    cursor.execute(sql3, "one_bedroom")
    one_bedroom = cursor.fetchall()

    sql4 = "select * from house_details where house_type = %s"
    cursor.execute(sql4, "two_bedroom")
    two_bedroom = cursor.fetchall()

    sql5 = "select * from house_details where house_type = %s"
    cursor.execute(sql5, "three_bedroom")
    three_bedroom = cursor.fetchall()

    print(singles)
    return render_template("home.html",   singles=singles, bedsitters=bedsitters, one_bedroom=one_bedroom, two_bedroom=two_bedroom, three_bedroom=three_bedroom)


@app.route('/upload', methods = ["GET", "POST"])
def upload():
    if request.method == "GET":
        return render_template("upload.html")
    else:
        house_number = request.form["house_number"]
        rent_amount = request.form["rent_amount"]
        house_type = request.form["house_type"]

        house_image = request.files["house_image"]
        house_image.save('static/images/' + house_image.filename)

        house_image_name = house_image.filename

        connection = pymysql.connect(host='localhost', user='root', password='', database='nekesa_rental')
        cursor = connection.cursor()
        sql = "insert into house_details (house_number, rent_amount, house_type, house_image_name) values(%s, %s, %s, %s)"
        cursor.execute(sql, (house_number, rent_amount, house_type, house_image_name))
        connection.commit()

        return render_template("upload.html", message = "Uploaded successfully")
    

@app.route('/single/<house_number>')
def single(house_number):
    connection = pymysql.connect(host='localhost', user='root', password='', database='nekesa_rental')
    cursor = connection.cursor()
    sql = "select * from house_details where house_number = %s"
    cursor.execute(sql, house_number)
    house  = cursor.fetchone()

    return render_template("single.html", house=house)


@app.route('/mpesa', methods = ["POST"])
def mpesa_payment():

    phone = request.form["phone"]
    amount = request.form["amount"]

    mpesa.stk_push(phone, amount)
    message = "<h3> Please complete payment in your phone</h3>"\
            "<a href='/'> Back to home</a>"
    return message


@app.route('/aboutus')
def aboutus():
    return render_template("aboutus.html")


@app.route('/admin')
def admin():
    return render_template("admin.html")
    

@app.route('/adminregister', methods = ["GET", "POST"])
def adminregister():
    if request.method == "GET":
        return render_template("adminregister.html")
    else:
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        password2 = request.form["password2"]
        hashed_password = hash_salt_password(password)


        if len(password) < 8:
            return render_template("adminregister.html", error = "Password is too short")
        elif password != password2:
            return render_template("adminregister.html", error = "Passwords do not match")
        else:
            connection = pymysql.connect(host='localhost', user='root', password='', database='nekesa_rental')
            cursor = connection.cursor()
            sql = "insert into admin (username, email, password) values(%s, %s, %s)"
            cursor.execute(sql, (username, email, hashed_password))
            connection.commit()

            return render_template("adminregister.html", message = "Added successfully")
        
@app.route('/adminlogin', methods = ["GET", "POST"])
def adminlogin():
    if request.method == "GET":
        return render_template("adminlogin.html")
    else:
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = hash_salt_password(password)

        connection = pymysql.connect(host='localhost', user='root', password='', database='nekesa_rental')
        cursor = connection.cursor()
        sql = "select * from admin where username = %s and password = %s"
        cursor.execute(sql, (username, hashed_password))

        if cursor.rowcount == 0:
            return render_template("adminlogin.html", error = "Invalid credentials")
        else:
            session ['key'] = username
            return redirect('/admin')


@app.route('/register', methods = ["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form["username"]
        email = request.form["email"]
        id_number = request.form["id_number"]
        telephone = request.form["telephone"]
        password = request.form["password"]
        password2 = request.form["password2"]
        hashed_password = hash_salt_password(password)

        if len(password) < 8:
            return render_template("register.html", error = "password is too short")
        elif password != password2:
            return render_template("register.html", error = "passwords do not match")
        else:
            connection = pymysql.connect(host='localhost', user='root', password='', database='nekesa_rental')
            cursor = connection.cursor()

            sql = "insert into users(username, email, id_number, telephone, password) values(%s,%s,%s,%s,%s)"
            cursor.execute(sql, (username, email, id_number, telephone, hashed_password))
            connection.commit()

            return render_template("register.html", message = "Registered successfully")


@app.route('/login', methods = ["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = hash_salt_password(password)

        connection = pymysql.connect(host='localhost', user='root', password='', database='nekesa_rental')
        cursor = connection.cursor()
        sql = "select * from users where username = %s and password = %s"
        cursor.execute(sql, (username, hashed_password))

        if cursor.rowcount == 0:
            return render_template("login.html", error = "Invalid credentials")
        else:
            session['key'] = username
            return redirect('/')
        
        
@app.route('/logout')
def logout():
    session.clear()
    return render_template("login.html")
        

if "__main__" == __name__:
    app.run(debug=True)