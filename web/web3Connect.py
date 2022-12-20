import eth_account
from web3 import Web3, HTTPProvider
import json


URL = "https://rpc.ankr.com/eth_goerli"
# URL="https://127.0.0.1:8545"
CS_ADDRESS= '0x31A2D5B68161a8fA006B24fb006E0Ec55E49257a'
TOKEN_ADDRESS='0x2b39D9D256a1e447D9568D121CB498a5DdE73482'




add='0x3753DF833840D8A8D4bd43803946992efDE3CdE9'

tokenpath='TokenAbi.json'
cspath='CryptoSurveyAbi.json'
with open(tokenpath, "r") as f:
    tokenAbi = json.load(f)
with open(cspath, "r") as cs:
  csAbi = json.load(cs)
    
w3 = Web3(Web3.HTTPProvider(URL))
    
# tokenContract = w3.eth.contract(address=w3.toChecksumAddress(TOKEN_ADDRESS), abi=tokenAbi)
# decimals=tokenContract.functions.decimals().call()
# balance=tokenContract.functions.balanceOf(w3.toChecksumAddress(add)).call()

# csk=float(balance)/10**decimals
# print(csk)
cryptoSurveyContract=w3.eth.contract(address=w3.toChecksumAddress(CS_ADDRESS), abi=csAbi)
surveyCount=cryptoSurveyContract.functions.getSurveyCount().call()
s=[]
for i in range(surveyCount):
    survey=cryptoSurveyContract.functions.getSurvey(i+1).call()
    temp={}
    temp['name']=survey[0]
    temp['isActive']=survey[1]
    temp['reward']=survey[2]
    temp['isLotto']=survey[3]
    temp['usercount']=survey[4]
    survey['id']=i+1
    if temp['isActive']:
        s.append(survey)



