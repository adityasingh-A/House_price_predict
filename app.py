from flask import Flask, render_template, request, redirect, session
import pickle
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.secret_key = "secret123"

model = pickle.load(open("model.pkl","rb"))
stats = pickle.load(open("stats.pkl","rb"))

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/register',methods=['POST'])
def register():
    user = request.form['username']
    password = request.form['password']

    with open("users.txt","a") as f:
        f.write(user + "," + password + "\n")

    return redirect('/')

@app.route('/login',methods=['POST'])
def do_login():
    user = request.form['username']
    password = request.form['password']

    if not os.path.exists("users.txt"):
        open("users.txt","w").close()

    with open("users.txt","r") as f:
        for line in f:
            u,p = line.strip().split(',')
            if u==user and p==password:
                session['user'] = user
                return redirect('/home')

    return "Invalid Login ❌"

@app.route('/home')
def home():
    if 'user' not in session:
        return redirect('/')
    return render_template('index.html')

@app.route('/predict',methods=['POST'])
def predict():

    if 'user' not in session:
        return redirect('/')

    area = int(request.form['area'])
    bedrooms = int(request.form['bedrooms'])
    bathrooms = int(request.form['bathrooms'])
    garage = int(request.form['garage'])

    location_type = request.form['location']
    city_name = request.form['city_name']

    prediction = model.predict([[area,bedrooms,bathrooms,garage]])[0]

    if area > 2000:
        prediction *= 1.25
    elif area < 800:
        prediction *= 0.85

    room_score = bedrooms + bathrooms
    prediction *= (1 + room_score * 0.04)

    prediction *= (1 + garage * 0.05)

    if location_type == "Low":
        prediction *= 0.7
    elif location_type == "Medium":
        prediction *= 1.1
    else:
        prediction *= 1.6

    if area > 3000 and location_type == "High":
        prediction *= 1.2

    low = prediction - stats["std"]
    high = prediction + stats["std"]

    if not os.path.exists("static"):
        os.makedirs("static")

    plt.figure()
    plt.bar(['Low','Predicted','High'],[low,prediction,high])
    plt.savefig("static/user_graph.png")
    plt.close()

    with open("history.txt","a",encoding="utf-8") as f:
        f.write(f"{session['user']} -> {int(prediction)} INR -> {city_name}\n")

    return render_template('index.html',
        prediction_text="₹ {:,.0f}".format(prediction),
        range_text="₹ {:,.0f} - ₹ {:,.0f}".format(low,high),
        show_graph=True)

@app.route('/history')
def history():
    if not os.path.exists("history.txt"):
        open("history.txt","w").close()

    with open("history.txt","r",encoding="utf-8") as f:
        data = f.readlines()

    return render_template('history.html',data=data)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)