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

    ltv = 0.8
    monthly_payment = 0


    def __init__(self, appraised_value, purchase_price, rent=0):
        self.purchase_price = appraised_value
        self.appraised_value = purchase_price
        self.rent = rent
    
    def set_rent(self, rent):
        self.rent = rent

    def set_prop_taxes(self, prop_taxes):
        self.prop_taxes = prop_taxes
    
    def set_insurance(self, insurance):
        self.insurance = insurance
    
    def set_interest_rate(self, interest_rate):
        self.interest_rate = interest_rate / 100
    
    def set_fee_rate(self, refi_fee_rate):
        self.refi_fee_rate = refi_fee_rate
    
    def set_ltv(self, ltv):
        self.ltv = ltv
    
    def set_monthly_payment(self, amoritization):
        self.monthly_payment = -npf.pmt(self.interest_rate/12, amoritization *12, self.appraised_value * self.ltv)

    def set_target_dscr(self, target_dscr):
        self.target_dscr = target_dscr
    
    def calculate_dscr(self):
        gross = self.rent * 12
        expenses = (gross * self.vacancy) + (gross * self.management) + (gross * self.maintenance)

        net = gross - expenses
        try:
            actual_dscr = net / (12 * self.monthly_payment)
            return actual_dscr
        except:
            return 0
    
    def determine_feasibility(self, actual_dscr):
        if actual_dscr >= self.target_dscr:
            return True
        return False
        