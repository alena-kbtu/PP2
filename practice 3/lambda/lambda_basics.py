class Acount:
    def __init__(self,owner,balance):
        self.owner = owner
        self.balance = balance
        self.bal_desc = str(balance)
    
    def upd_bal_desc(self, bad_with):
        if(bad_with):
            self.bal_desc = "insufficient funds"
        else:
            self.bal_desc = str(self.balance)
    
    def deposit(self, amount):
        self.balance+=amount
        self.upd_bal_desc(False)
        
    
    def withdraw(self,amount):
        if(amount>self.balance):
            self.upd_bal_desc(True)
        else:
            self.balance-=amount
            self.upd_bal_desc(False)
    
    def __str__(self):
        return self.bal_desc
    
s = input().split()
arg1 = int(s[0])
arg2 = int(s[1])
acc1 = Acount("Zhandos",arg1)
acc1.withdraw(arg2)
print(acc1)