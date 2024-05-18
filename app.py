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

test = default_config['test']

@app.route('/calculate_dscr')
def my_form():
    return render_template('refinance.html',
                           pp_value = "100000", 
                           ap_value = "150000", 
                           rent_value = "1500",
                           taxes_value = "500",
                           insurance_value = "500",
                           interest_rate_value = "7.5")

@app.route('/calculate_dscr', methods=['POST'])
def my_form_post():
    purchase_price = int(request.form['purchase_price'])
    appraised_value = int(request.form['appraised_value'])
    target_rent = int(request.form['target_rent'])
    refi = Refinance(purchase_price=purchase_price, appraised_value=appraised_value, rent=target_rent)
    refi.set_insurance(int(request.form['insurance']))
    refi.set_prop_taxes(int(request.form['taxes']))
    refi.set_interest_rate(float(request.form['interest_rate']))
    
    refi.set_monthly_payment(amoritization=25)
    actual_dscr = refi.calculate_dscr()
    return render_template("refinance.html",  
                           pp_value = purchase_price, 
                           ap_value = appraised_value, 
                           rent_value = target_rent,
                           taxes_value = refi.prop_taxes,
                           insurance_value = refi.insurance,
                           interest_rate_value = refi.interest_rate,
                           MONTHLY_PAYMENT = refi.monthly_payment,
                           DSCR_RATIO = f"DSCR: {actual_dscr}", 
                           FEASIBILITY = f" Feasible?: {refi.determine_feasibility(actual_dscr=actual_dscr)}")



@app.route("/", methods=['GET', 'POST'])
def func():
    refi = Refinance(150000, 180000, 1500)
    return f"<p>Hello, World! {refi.calculate_dscr()}</p>"


def refi_calculate(appraised_value, original_purchase_price, current_equity):
    return

if __name__ == '__main__':
    app.run()
