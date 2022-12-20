#!/usr/bin/env python3.8

import os
import random
import eth_account
import web3
from web3 import Web3, HTTPProvider
from flask import Flask, request, render_template, g, redirect, Response,session
import datetime
from datetime import timedelta
import json
import time

tmpl_dir=os.path.dirname(os.path.abspath(__file__))
# app = Flask(__name__, template_folder=tmpl_dir)
app = Flask(__name__, template_folder = '.',static_folder='',static_url_path='')
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)




# URL = "https://rpc.sepolia.dev"
URL = "https://rpc.ankr.com/eth_goerli"
# URL="https://127.0.0.1:8545"
CS_ADDRESS= '0x25a1a4cb20Aec4C93Cf3C6C37D40a36A64B0A225'
TOKEN_ADDRESS='0xfe18Aedf6a3e9F6C4c2894dbC6A85b32a53d45D9'
OWNER_ADDRESS='0x3753DF833840D8A8D4bd43803946992efDE3CdE9'
DICIMAL=18






@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  print(request.args.__str__())

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  # try:
  #   g.conn.close()
  # except Exception as e:
  #   pass
  pass


@app.route('/')
def index():
    context = dict(data = [''])

    return render_template("index.html",**context)


# @app.route('/')
def templete_index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)


  context = {}

  return render_template("index.html", **context)





 


@app.route('/stop',methods=['POST'])
def stop():
  survey_id= int(request.form.get('id'))
  userAddress=session['address']

  cspath='CryptoSurveyAbi.json'
  with open(cspath, "r") as cs:
    csAbi = json.load(cs)
    
  w3 = Web3(Web3.HTTPProvider(URL))
  cryptoSurveyContract=w3.eth.contract(address=w3.toChecksumAddress(CS_ADDRESS), abi=csAbi)
  tx=cryptoSurveyContract.functions.claimReward(survey_id).build_transaction({'from':userAddress,'gas': 359000,'nonce': w3.eth.get_transaction_count(userAddress)})
  signed_txn = w3.eth.account.sign_transaction(tx, session['privatekey'])
  w3.eth.send_raw_transaction(signed_txn.rawTransaction)

  
    

  return redirect('/mainpage')
  


@app.route('/create',methods=['POST'])
def create():
  # string memory pName, 
  # bool pIsLotto, 
  # uint256 pReward, 
  # uint256 surveyDuration, 
  # uint256 enteranceFee
  name = str(request.form.get('name'))
  reward = int(request.form.get('reward'))*10**DICIMAL
  isLotto = 0
  if request.form.get('isLotto')=='yes':
    isLotto=True
  else:
    isLotto=False
  
  duration=int(request.form.get('duration'))
  enteranceFee=int(request.form.get('enteranceFee'))*10**DICIMAL


  userAddress=session['address']
  cspath='CryptoSurveyAbi.json'
  with open(cspath, "r") as cs:
    csAbi = json.load(cs)
    
  w3 = Web3(Web3.HTTPProvider(URL))
  cryptoSurveyContract=w3.eth.contract(address=w3.toChecksumAddress(CS_ADDRESS), abi=csAbi)
  tx=cryptoSurveyContract.functions.createSurvey(name,isLotto, reward,duration,enteranceFee).build_transaction({'from':userAddress,'gas': 359000,'nonce': w3.eth.get_transaction_count(userAddress)})
  signed_txn = w3.eth.account.sign_transaction(tx, session['privatekey'])
  w3.eth.send_raw_transaction(signed_txn.rawTransaction)



  return redirect('/mainpage')

@app.route('/report',methods=['POST'])
def report():
  survey_id= int(request.form.get('id'))
  userAddress=session['address']

  cspath='CryptoSurveyAbi.json'
  with open(cspath, "r") as cs:
    csAbi = json.load(cs)
    
  w3 = Web3(Web3.HTTPProvider(URL))
  cryptoSurveyContract=w3.eth.contract(address=w3.toChecksumAddress(CS_ADDRESS), abi=csAbi)
  tx=cryptoSurveyContract.functions.report2Survey(survey_id).build_transaction({'from':userAddress,'gas': 359000,'nonce': w3.eth.get_transaction_count(userAddress)})
  signed_txn = w3.eth.account.sign_transaction(tx, session['privatekey'])
  w3.eth.send_raw_transaction(signed_txn.rawTransaction)



  
  return redirect('/mainpage')

@app.route('/mainpage')
def mainpage():
  # name: pName,
  # isActive: true,
  # reward: pReward,
  # isLotto: pIsLotto,
  # enteranceFee: enteranceFee,
  # surveyEndTime: block.timestamp + surveyDuration * 1 minutes,
  # userCount:0
  tokenpath='TokenAbi.json'
  cspath='CryptoSurveyAbi.json'
  with open(tokenpath, "r") as f:
    tokenAbi = json.load(f)
  with open(cspath, "r") as cs:
    csAbi = json.load(cs)
    
  w3 = Web3(Web3.HTTPProvider(URL))
    
  tokenContract = w3.eth.contract(address=w3.toChecksumAddress(TOKEN_ADDRESS), abi=tokenAbi)
  balance=tokenContract.functions.balanceOf(w3.toChecksumAddress(session['address'])).call()
  decimals=tokenContract.functions.decimals().call()
  csk=float(balance)/10**decimals
  cryptoSurveyContract=w3.eth.contract(address=w3.toChecksumAddress(CS_ADDRESS), abi=csAbi)
  surveyCount=cryptoSurveyContract.functions.getSurveyCount().call()
  s=[]
  for i in range(surveyCount):
    survey=cryptoSurveyContract.functions.getSurvey(i+1).call()
    temp={}
    temp['name']=survey[0]
    temp['isActive']=survey[1]
    temp['reward']=float(survey[2])/10**DICIMAL
    temp['isLotto']=survey[3]
    temp['enteranceFee']=float(survey[4])/10**DICIMAL
    temp['surveyEndTime']=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(survey[5]))
    temp['usercount']=survey[6]
    temp['id']=i+1
    if temp['isActive']:
      s.append(temp)



  context = {}
  context['data']=s
  context['isOwner']=session['isOwner']
  session['csk']=csk
  session['surveys']=s

  




  return render_template("mainPage.html",**context)

@app.route('/login',methods=['POST'])
def login():

    
    session['account']=None
    session['privatekey']=None
    session['csk']=None
    # session['tokencontract']=None

    privatekey = request.form.get('privatekey')
    acc = eth_account.Account.from_key(private_key=privatekey)
    web3.eth.defaultAccount=acc
    # print(acc.address)

    # web3.eth.accounts.wallet.add(privatekey)

    # print(tokenContract.all_functions())
    # print(cryptoSurveyContract.all_functions())
    if acc.address==OWNER_ADDRESS:
      session['isOwner']=True
    else:
      session['isOwner']=False
    
    session['address']=acc.address
    session['privatekey']=privatekey
    

        
    return redirect('/mainpage')
   



if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """
    port=84
    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()