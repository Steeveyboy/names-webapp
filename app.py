from flask import Flask, render_template, request, redirect
import dbWrapper

app = Flask(__name__)

dbm = dbWrapper.dbManager()

# @app.route("/")
# def landing():
#     return render_template("index.html")

@app.route("/searchName/<name>", methods=["GET"])
def getName(name):
    results = dbm.get_name(name)
    print(name)
    # print(request.form['searchText'])
    return results

