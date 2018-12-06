#!usr/bin/env python3

from flask import Flask, render_template, request, redirect, session, jsonify, url_for, escape
import model

app = Flask(__name__)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Qhgvf8z\n\xec]/'

#----------------------------------------------------------------------------------------
@app.route('/go', methods=['GET'])
def start():
    if request.method == 'GET':
        return render_template('go.html')

@app.route('/')
def index():
    if 'username' in session:
        return redirect("/dashboard")
    return redirect("/go")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        session['username'] = request.form['username']
        username = request.form['username']
        password = request.form['password']
        suc=model.create_user(username,password)
        if suc:
            return redirect(url_for('index'))
        else:
            return render_template('register.html', message='Username Taken')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']
        session['username'] = request.form['username']
        if model.check_user(username,password):
            return redirect(url_for('index'))
        else:
            return render_template('login.html', message='Login error')

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect('/go')

@app.route('/options', methods=['GET'])
def options():
    if request.method == 'GET':
        return render_template('options.html')

@app.route("/quote", methods = ['GET', 'POST'])
def quote():
    
    if request.method == 'GET':
        return render_template('dashboard.html')
    else:
        user_name='%s' % escape(session['username'])
        quote = request.form['quote']
        price=model.quote(quote)
        info = model.dashboard(user_name)
        if price:
            return render_template('dashboard.html', quote_info = quote+': '+str(price), info=info)
        else:
            return render_template('dashboard.html', quote_info='Could not find quote', info=info)

    
@app.route("/lookup", methods = ['GET', 'POST'])
def lookup():
    if request.method == 'GET':
        return render_template('dashboard.html')
    else:
        user_name='%s' % escape(session['username'])
        info = model.dashboard(user_name)
        company = request.form['lookup']
        ticker=model.lookup(company)
        if ticker:
            return render_template('dashboard.html', lookup_info = company+': '+ ticker, info=info)
        else:

            return render_template('dashboard.html', lookup_info='Could not find Ticker for '+ company, info=info)

@app.route("/deposit", methods = ['GET', 'POST'])
def deposit():
    user_name='%s' % escape(session['username'])
    if request.method == 'GET':
        return render_template('dashboard.html')
    else:
        try: 
            deposit = int(request.form['deposit'])
        except:
            deposit = float(request.form['deposit'])
        
        money=model.deposit(user_name, deposit)
        info = model.dashboard(user_name)
        if money:
            return render_template('dashboard.html', deposit_info = "Deposited: $"+ str(deposit),info=info)
        else:
            return render_template('dashboard.html', deposit_info= money, info=info)


@app.route("/buy", methods = ['GET', 'POST'])
def buy():
    if request.method == 'GET':
        return render_template('dashboard.html')
    else:
        
        Ticker = request.form['Ticker']
        Shares = int(request.form['Shares'])
        user_name='%s' % escape(session['username'])
        #buy=model.buy(Ticker,Shares, user_name)
        info = model.dashboard(user_name)
        if request.form.get('inlineCheckbox1'):
            buy=model.buy(Ticker,Shares, user_name)
            info = model.dashboard(user_name)
            if buy:
                mes= buy['User']+' bought '+ str(buy['Shares']) + ' share(s) of '+buy['Ticker']+ ' for '+  str(buy['Cost'])
                return render_template('dashboard.html', buy_info = mes, info=info)
            else:
                mes= "You don't have enough money"
                return render_template('dashboard.html', buy_info= mes, info=info) 
        elif request.form.get('inlineCheckbox2'):
            sell=model.sell(Ticker,Shares, user_name)
            info = model.dashboard(user_name)
            if sell:
                message= sell['username']+' sold '+ str(sell['Shares']) + ' shares of '+sell['Ticker']+ ' for '+  str(sell['Cost'])
                return render_template('dashboard.html', sell_info = message, info=info)
            else:
                message= "You don't have enough shares"
                return render_template('dashboard.html', sell_info=message, info=info)
        else:
            mes="Click Buy or Sell box"
            return render_template('dashboard.html', buy_info= mes, info=info)

@app.route("/sell", methods = ['GET', 'POST'])
def sell():
    if request.method == 'GET':
        return render_template('dashboard.html')
    else:
        Ticker = request.form['Ticker']
        Shares = int(request.form['Shares'])
        user_name='%s' % escape(session['username'])
        sell=model.sell(Ticker,Shares, user_name)
        info = model.dashboard(user_name)
        if sell:
            message= sell['username']+' sold '+ str(sell['Shares']) + ' shares of '+sell['Ticker']+ ' for '+  str(sell['Cost'])
            return render_template('dashboard.html', sell_info = message, info=info)
        else:
            message= "You don't have enough shares"
            return render_template('dashboard.html', sell_info=message, info=info)   


@app.route("/dashboard", methods = ['GET'])
def dashboard():
    if request.method == 'GET':
        user_name='%s' % escape(session['username'])
        info = model.dashboard(user_name)
        return render_template('dashboard.html', info=info)
    
    


if __name__=="__main__":
    app.run(debug=True)