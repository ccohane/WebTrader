#!/usr/bin/env python3
from wrapper import Markit
#import mapper
import wrapper
from orm import Database
import time
import uuid
import copy


def quote(ticker):
    with Markit(ticker) as m:
        try:
            price=m.quote()
            quota=ticker+ " price = $"+str(price)
            return price
        except:
            print("\nDid not find ticker")
            return 0

def lookup(company_name):
    with Markit(company_name) as m:
        return m.lookup()


def buy(ticker,shares,user_name):
    '''
    Look into Database to see
    '''
    balance=int(get_balance(user_name))
    print(balance)

    price = quote(ticker)
    if(price==0):
        return False
    total_cost = price * int(shares)

    if(balance >= total_cost):
        if(lookup_database(ticker, user_name)==False):
            insert_database(ticker,shares, user_name)
            balance -= total_cost
            update_balance(user_name, balance)
            trade="\nYou bought "+str(shares)+" shares of "+str(ticker)+" for "+str(total_cost)
            record_transaction(user_name, trade)
            return {"User" : user_name , "Ticker": ticker, "Shares": shares, "Cost" : total_cost}
        else:
            total_shares=shares+lookup_database(ticker , user_name)
            update_database(ticker, total_shares , user_name)
            balance -= total_cost
            update_balance(user_name, balance)
            trade="\nYou bought "+str(shares)+" shares of "+str(ticker)+" for "+str(total_cost)
            record_transaction(user_name, trade)
            return {"User" : user_name , "Ticker": ticker, "Shares": shares, "Cost" : total_cost}
    else:
        return False
        

    #print_holdings(user_name)


def sell(ticker, shares, user_name):
    price = quote(ticker)
    total_shares=lookup_database(ticker, user_name)
    balance=get_balance(user_name)

    if total_shares==False:
        return "You do not have any shares "
    else:

        if(total_shares>=shares):

            total_amount= price *shares
            numShares=total_shares-shares
            update_database(ticker, numShares, user_name)
            balance+=total_amount
            update_balance(user_name,balance)
            trade="\nYou sold "+str(shares)+" shares of "+str(ticker)+" for "+str(total_amount)
            record_transaction(user_name,trade)
            return {"username":user_name, "Ticker": ticker, "Shares": shares, "Cost": total_amount}
        else:
            return "You don't own enough shares"

    #print_holdings(user_name)


def deposit(user_name,deposit):
    with Database() as db:
        transaction="You deposited $"+str(deposit)+" into your account."
        record_transaction(user_name,transaction)

        db.c.execute('''SELECT available_balance FROM balance 
                        WHERE user_name ='{}';'''.format(user_name))
        balance=db.c.fetchone()

        db.c.execute('''SELECT original_deposits FROM balance 
                        WHERE user_name ='{}';'''.format(user_name))
        orig_deposits=db.c.fetchone()

        if balance and orig_deposits:
            new_deposit=orig_deposits[0]+float(deposit)
            new_balance=balance[0] + float(deposit)
            db.c.execute('''UPDATE balance SET available_balance = {}, original_deposits={} 
                            WHERE user_name = '{}';'''.format(new_balance, new_deposit , user_name))
            return 1
        else:
            db.c.execute('''INSERT INTO balance(user_name, available_balance, original_deposits) 
                            VALUES('{}',{},{});'''.format(user_name,deposit,deposit))
            return 1

def create_table():
    with Database() as db:
        db.c.execute('''CREATE TABLE IF NOT EXISTS balance(
                        pk INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_name VARCHAR,
                        available_balance FLOAT,
                        original_deposits FLOAT);''')

        db.c.execute('''CREATE TABLE IF NOT EXISTS Holdings(
                        pk INTEGER PRIMARY KEY AUTOINCREMENT,
                        Stocks VARCHAR,
                        numShares INTEGER,
                        user_name VARCHAR);''')

        db.c.execute('''CREATE TABLE IF NOT EXISTS users(
                        pk INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_names VARCHAR,
                        password VARCHAR,
                        apikey VARCHAR,
                        admin BOOL);''')

        db.c.execute('''CREATE TABLE IF NOT EXISTS transactions(
                        pk INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_names VARCHAR,
                        history VARCHAR);''')

def record_transaction(user_name, trade):
    with Database() as db:
        db.c.execute('''INSERT INTO transactions(user_names,history)
                        VALUES('{}','{}');'''.format(user_name,trade))

def print_transactions(user_name):
    with Database() as db:
        db.c.execute('''SELECT history FROM transactions WHERE user_names='{}';'''.format(user_name))
        trades=db.c.fetchall()
        dict={}
        for x in range(len(trades)):
            dict["Transaction "+str(x)]=trades[x][0]

        return(dict)

def lookup_database(stock, user_name):
    with Database() as db:
        db.c.execute('''SELECT numShares FROM Holdings
                        WHERE Stocks='{}' AND user_name='{}';'''.format(stock.upper(),user_name))
        result=db.c.fetchone()
        if result:
            return result[0]
        else:
            return False


def insert_database(stock, shares, user_name):
    with Database() as db:
        db.c.execute('''INSERT INTO Holdings(Stocks,numShares,user_name) 
                        Values('{}',{},'{}');'''.format(stock.upper(),shares,user_name))


def update_database(stock, shares,user_name):
    with Database() as db:
        db.c.execute('''UPDATE Holdings SET numShares={} WHERE Stocks='{}' 
                        AND user_name='{}';'''.format(shares,stock.upper(),user_name)) 


def create_user(user_name , password):

    with Database() as db:
        create_table()
        user_name_taken = check_user_exist(user_name)

        if user_name_taken==False:
            apikey= str(uuid.uuid4())
            admin_=admin()
            sql='''INSERT INTO users(user_names,password,apikey,admin) 
                            Values(?,?,?,?);'''
            db.c.execute(sql, (user_name, password, apikey, admin_))
            return True
        else:
            return False

def api_authenticate(apikey):
    with Database() as db:
        sql='''SELECT user_names FROM users WHERE apikey=?;'''
        db.c.execute(sql,(apikey,))
        result=db.c.fetchone()
        if result:
            return result[0]
        else:
            return False

def get_status(user_name):
    with Database() as db:
        db.c.execute('''SELECT admin FROM users WHERE user_names='{}';'''.format(user_name))
        result=db.c.fetchone()

        if result:
            return result[0]
        else:
            return False

def admin():
    with Database() as db:
        db.c.execute('''SELECT * FROM users;''')
        rows=db.c.fetchall()
        if len(rows)==0:
            return 1
        else:
            return 0

def check_user_exist(user_name):
    with Database() as db:
        db.c.execute('''SELECT * FROM users WHERE user_names='{}';'''.format(user_name))
        result=db.c.fetchone()

        if result:
            return True
        else:
            return False


def check_user(user_name, password):
    with Database() as db:
        db.c.execute('''SELECT * FROM users WHERE user_names='{}'
                        AND password='{}';'''.format(user_name, password))
        result=db.c.fetchone()

        if result:
            return True
        else:
            return False


def update_balance(user_name, amount):
    with Database() as db:
        db.c.execute('''UPDATE balance SET available_balance={}
                        WHERE user_name='{}';'''.format(amount,user_name))


def get_balance(user_name):
    with Database() as db:
        db.c.execute('''SELECT available_balance FROM balance
                        WHERE user_name='{}';'''.format(user_name))
        result=db.c.fetchone()
        if result:
            return result[0]
        else:
            return 0

def print_holdings(user_name):
    with Database() as db:
        db.c.execute('''SELECT * FROM Holdings WHERE user_name='{}';'''.format(user_name))
        list=db.c.fetchall()
        dict={}
        if list:
            for x in list:
                dict[x[1]]={"Shares": str(x[2]), "Equity": str(quote(x[1])*x[2])}
        else:
            dict.update({"No Stocks Owned":False})
        return(dict)

def get_total_equity(user_name):
    with Database() as db:
        db.c.execute('''SELECT * FROM Holdings WHERE user_name='{}';'''.format(user_name))
        list=db.c.fetchall()
        total_equity=0
        if list:
            for x in list:
                total_equity+=quote(x[1])*x[2]
        else:
            print("\nNo Stocks Owned")
        return total_equity

def get_original_deposits(user_name):
    with Database() as db:
        db.c.execute('''SELECT original_deposits FROM balance
                        WHERE user_name='{}';'''.format(user_name))
        result=db.c.fetchone()
        if result:
            return result[0]
        else:
            return 0
def get_percentage_gain(user_name):
    total_port=get_balance(user_name)+get_total_equity(user_name)
    orig=get_original_deposits(user_name)
    if orig==0:
        return 0
    return ((total_port-orig)/orig)*100

def dashboard(user_name):
    
    dash={
        "Username": user_name,
        "Total Portfolio Value": get_balance(user_name)+get_total_equity(user_name), 
        "Available cash": get_balance(user_name),
        "Total Equity": get_total_equity(user_name),
        "Percentage Gain/Loss": get_percentage_gain(user_name),
        "Holdings": print_holdings(user_name),
        "Transaction History": print_transactions(user_name)
    }
    return(dash)

def get_leaderboards():
    with Database() as db:
        db.c.execute('''SELECT user_names FROM users WHERE admin=0;''')
        list_users=db.c.fetchall()
        leaderboard=[]
        print(list_users)
        for x in list_users:
            leaderboard.append((x[0],get_percentage_gain(x[0])))

        leaderboard.sort(key=lambda tup: tup[1],reverse=True)
        count=0
        for x in leaderboard:
            print("User: "+x[0] +". Percentage Gain or Loss: "+ str(x[1]))
            count+=1
            if(count ==10):
                break
        time.sleep(10)
