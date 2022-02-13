import json
import urllib.request
import web3

from etherscan import Etherscan

from web3 import Web3
from ens.auto import ENS

import mysql.connector
from mysql.connector import errorcode

import sys


print ("ENS-Work")

# Initializing Params
eth_key = "7I39Q4ZZ6SER7ZZTKQMNGYHD3UTZ6BSQ32"
eth_contract = "0x084b1c3c81545d370f3634392de611caabff8148"
my_config = {
  'user': 'ens_user',
  'password': 'ens_password',
  'host': 'localhost',
  'database': 'ens',
  'raise_on_warnings': True
}

# Initializing Etherscan API
eth = Etherscan(eth_key)

# Initialising WEB3 ENS
w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/e1aff836d3a64d6aba0f028217da381f"))
ns = ENS.fromWeb3(w3)

# initializing MySQL connection

try:
  my_cn = mysql.connector.connect(**my_config)
except mysql.connector.Error as err:
    print(err)
    quit()
else:
  print ("Connected to the Database")

cursor =  my_cn.cursor()
# Functio Reads First block    
def getBlock():
    #read block number
    q_block = "SELECT block from ens.block"
    cursor.execute(q_block)
    for (block) in cursor:
        start_block = block
    return start_block[0]

# Function updates last blosk
def updateBlock(block):
    u_block = "update ens.block set block = %s"
    cursor.execute(u_block,[block])
    my_cn.commit()

# Function updates reverse registry table
def updateName(domain, address):
    i_name = "insert into rev_registry (addr, name) values (%s, %s)"
    u_name = "update rev_registry set name = %s where addr = %s"
    d_name = "delete from rev_registry where addr = %s"
    if domain == "None":
        # delete name from the registry
        cursor.execute(d_name, [address])
        my_cn.commit()
    else:
        # insert or update
        
        try:
            # attempt to insert
            cursor.execute(i_name, [address, domain])
        except mysql.connector.Error as err:
            # update if record is there
            if err.errno == 1062:
                cursor.execute(u_name, [domain, address])
            else:
                print (err)
                quit()
        finally:
            my_cn.commit()
        
   



# Get transactions
#req = urllib.request.urlopen('https://api.etherscan.io/api?module=account&action=txlist&address=0x084b1c3c81545d370f3634392de611caabff8148&sort=desc&apikey=7I39Q4ZZ6SER7ZZTKQMNGYHD3UTZ6BSQ32')
url ='https://api.etherscan.io/api?module=account&action=txlist&address='+eth_contract+'&startblock='+str(getBlock())+'&sort=asc&apikey='+eth_key
req = urllib.request.urlopen(url)
resp = req.read()
tr = json.loads(resp)

# update block
end_block = tr["result"][-1]["blockNumber"]

print ("First block: "+ str(getBlock()))
print ("Last block: "+ str(end_block))

updateBlock(end_block)

for txh in tr["result"]:
    domain = ns.name(txh["from"])
    print(txh["from"], " --- ", domain, " --- ", txh["blockNumber"])
    # update
    updateName(str(domain), str(txh["from"]))




cursor.close()
my_cn.close()