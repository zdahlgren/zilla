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
                           equity_value = round(int(default_config["purchase_price"]) * 0.25),
                           rent_value = default_config["rent"],
                           taxes_value = default_config["taxes"],
                           insurance_value = default_config["insurance"],
                           interest_rate_value =default_config["interest_rate"],
                           ltv =default_config["ltv"])

@app.route('/calculate_dscr', methods=['POST'])
def my_form_post():
    purchase_price = int(request.form['purchase_price'])
    appraised_value = int(request.form['appraised_value'])
    equity = int(request.form['equity'])

    target_rent = int(request.form['target_rent'])
    refi = Refinance(purchase_price=purchase_price, appraised_value=appraised_value, equity=equity, rent=target_rent)
    refi.set_insurance(int(request.form['insurance']))
    refi.set_prop_taxes(int(request.form['taxes']))
    refi.set_interest_rate(float(request.form['interest_rate']))
    refi.set_ltv(float(request.form['ltv']))
    
    refi.set_monthly_payment(amoritization=int(default_config["amoritization"]))
    refi.set_gross_net_and_expenses()
    actual_dscr = refi.calculate_dscr()

    workable_scenarios = ""
    happy_net = ""
    happy_rent = "" 
    happy_monthly_payment = ""
    happy_ltv = ""
    cashout = ""
    if not refi.is_feasible(actual_dscr):
        happy_tup = refi.happy_path_scenarios(amoritization=int(default_config["amoritization"]))
        workable_scenarios = f"To make numbers work at {refi.target_dscr} DSCR, you would need one of the following:" 
        happy_net = f"Yearly Net: ${round(happy_tup[0], 2)}" 
        new_total_rent = round(happy_tup[1], 2)
        increase = round(new_total_rent - round(refi.rent,2), 2)
        happy_rent = f"Monthly Rent: ${new_total_rent} (increase of ${increase})" 
        happy_monthly_payment = f"Monthly Payment: ${round(happy_tup[2], 2)}"
        happy_ltv = f"LTV: {round(happy_tup[3]*100, 2)}%"
    else:
        cashout_amount = (refi.appraised_value - refi.purchase_price) - ( (refi.appraised_value * (1-refi.ltv) - refi.equity)) - (refi.appraised_value * refi.refi_fee_rate)
        if cashout_amount > 0:
            cashout = f"Cashout: ${round(cashout_amount, 2)}"
        else:
            cashout = f"Warning! You won't be able to pull any cash out of this property"

    return render_template("refinance.html",  
                           pp_value = purchase_price, 
                           ap_value = appraised_value,
                           equity_value = equity,  
                           rent_value = target_rent,
                           taxes_value = refi.prop_taxes,
                           insurance_value = refi.insurance,
                           interest_rate_value = refi.interest_rate,
                           ltv = refi.ltv,
                           MORTGAGE_PAYMENT = f"Monthly Mortgage Payment: ${round(refi.mortgage, 2)}",
                           TOTAL_PAYMENT = f"Total Monthly Payment: ${round(refi.monthly_payment, 2)}",
                           GROSS = f"Yearly Gross: ${round(refi.gross, 2)}",
                           EXPENSES = f"Yearly Expenses: ${round(refi.expenses, 2)}",
                           NET = f"Yearly Net: ${round(refi.net, 2)}",
                           CASH_ON_CASH_RETURNS = f"Cash on Cash: {round(refi.calculate_cash_on_cash(), 2)}%",
                           DSCR_RATIO = f"DSCR: {round(actual_dscr, 2)}", 
                           FEASIBILITY = f"Feasible?: {refi.is_feasible(actual_dscr=actual_dscr)}",
                           CASHOUT = cashout,
                           WORKABLE_SCENARIOS = workable_scenarios,
                           HAPPY_NET = happy_net,
                           HAPPY_RENT = happy_rent,
                           HAPPY_MONTHLY_PAYMENT = happy_monthly_payment,
                           HAPPY_LTV = happy_ltv
                           )

@app.route("/", methods=['GET', 'POST'])
def func():
    return render_template("welcome.html")


if __name__ == '__main__':
    app.run()
