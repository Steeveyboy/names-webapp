from flask import Flask, render_template, request, redirect
import dbWrapper

app = Flask(__name__)

dbm = dbWrapper.dbManager()


@app.route("/searchName/<name>", methods=["GET"])
def getName(name):
    results = dbm.get_name(name)
    
    return results

