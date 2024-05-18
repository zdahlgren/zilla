import numpy_financial as npf
class Refinance:
    prop_taxes = 0
    insurance = 0
    
    rent = 0
    vacancy = 0.05
    management = 0.05
    maintenance = 0.05
    target_dscr = 1.2
    refi_fee_rate = 0.03

    ltv = 0.80
    monthly_payment = 0

    gross = 0
    net = 0
    expenses = 0


    def __init__(self, purchase_price, appraised_value, equity, rent=0):
        self.purchase_price = purchase_price
        self.equity = equity
        self.appraised_value = appraised_value
        self.rent = rent
    
    def set_rent(self, rent):
        self.rent = rent

    def set_prop_taxes(self, prop_taxes):
        self.prop_taxes = prop_taxes
    
    def set_insurance(self, insurance):
        self.insurance = insurance
    
    def set_interest_rate(self, interest_rate):
        self.interest_rate = interest_rate

    def set_fee_rate(self, refi_fee_rate):
        self.refi_fee_rate = refi_fee_rate
    
    def set_ltv(self, ltv):
        self.ltv = ltv
    
    def set_monthly_payment(self, amoritization):
        self.monthly_payment = -npf.pmt((self.interest_rate / 100)/12, amoritization *12, self.appraised_value * self.ltv)
        self.monthly_payment += (self.insurance/12)
        self.monthly_payment += (self.prop_taxes/12)

    def set_target_dscr(self, target_dscr):
        self.target_dscr = target_dscr
    
    def set_gross_net_and_expenses(self):
        self.gross = self.rent * 12
        self.expenses = (self.gross * self.vacancy) + (self.gross * self.management) + (self.gross * self.maintenance)
        self.net = self.gross - self.expenses

    def calculate_dscr(self):
        self.set_gross_net_and_expenses()
        try:
            actual_dscr = self.net / (12 * self.monthly_payment)
            return actual_dscr
        except:
            return 0
        
    def happy_path_scenarios(self, amoritization):
        self.set_gross_net_and_expenses()
        happy_net = (12 * self.monthly_payment) * self.target_dscr
        happy_rent_increase = (happy_net - self.net) / 12
        happy_monthly_payment = (self.net / self.target_dscr ) /12
        happy_ltv = self.find_happy_ltv(self.ltv, amoritization, happy_monthly_payment)
        return(happy_net, happy_rent_increase, happy_monthly_payment, happy_ltv)
    
    def find_happy_ltv(self, ltv, amoritization, happy_monthly_payment):
        value = -npf.pmt((self.interest_rate / 100)/12, amoritization *12, self.appraised_value * ltv) 
        value += (self.insurance/12) 
        value += (self.prop_taxes/12)
        if happy_monthly_payment < value:
            happy_ltv = self.find_happy_ltv((ltv - 0.05), amoritization+10, happy_monthly_payment)
        else:
            happy_ltv = ltv
        return happy_ltv
    
    def calculate_cash_on_cash(self):
        income = self.net - self.monthly_payment*12
        invested = (self.appraised_value * (1.0- self.ltv)) + (self.appraised_value*self.refi_fee_rate)
        return (income / invested)*100

    def is_feasible(self, actual_dscr):
        return actual_dscr >= self.target_dscr
        