from flask import Flask, render_template, request, jsonify
import os
import configparser
import requests
from requests.auth import HTTPBasicAuth
import json
import pathlib
from refinance import Refinance

app = Flask(__name__)
pwd = pathlib.Path(__file__).parent.absolute()
config = configparser.ConfigParser()
config.read(pwd / "conf/app.ini")
default_config = config['DEFAULT']

@app.route('/calculate_dscr')
def my_form():
    return render_template('refinance.html',
                           pp_value = default_config["purchase_price"], 
                           ap_value = default_config["appraised_value"], 
                           rent_value = default_config["rent"],
                           taxes_value = default_config["taxes"],
                           insurance_value = default_config["insurance"],
                           interest_rate_value =default_config["interest_rate"])

@app.route('/calculate_dscr', methods=['POST'])
def my_form_post():
    purchase_price = int(request.form['purchase_price'])
    appraised_value = int(request.form['appraised_value'])
    target_rent = int(request.form['target_rent'])
    refi = Refinance(purchase_price=purchase_price, appraised_value=appraised_value, rent=target_rent)
    refi.set_insurance(int(request.form['insurance']))
    refi.set_prop_taxes(int(request.form['taxes']))
    refi.set_interest_rate(float(request.form['interest_rate']))
    
    refi.set_monthly_payment(amoritization=int(default_config["amoritization"]))
    actual_dscr = refi.calculate_dscr()
    return render_template("refinance.html",  
                           pp_value = purchase_price, 
                           ap_value = appraised_value, 
                           rent_value = target_rent,
                           taxes_value = refi.prop_taxes,
                           insurance_value = refi.insurance,
                           interest_rate_value = refi.interest_rate,
                           MONTHLY_PAYMENT = f"Monthly Payment: ${round(refi.monthly_payment, 2)}",
                           CASH_ON_CASH_RETURNS = f"Cash on Cash: {round(refi.calculate_cash_on_cash(), 2)}%",
                           DSCR_RATIO = f"DSCR: {round(actual_dscr, 2)}", 
                           FEASIBILITY = f" Feasible?: {refi.determine_feasibility(actual_dscr=actual_dscr)}")

@app.route("/", methods=['GET', 'POST'])
def func():
    return f"<p>Sup brah</p>"


if __name__ == '__main__':
    app.run()
