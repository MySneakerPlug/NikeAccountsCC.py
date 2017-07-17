#Script to add billing info in a list of nike+ accounts
#Works for Nike US and Nike GB
#The account file should contain email:password in each line for each account

ACCOUNTFILENAME="nikeaccounts.txt"



COUNTRY="US"
FIRSTNAME="John"
LASTNAME="Doe"
ADDRESSLINE1="123 abcd street"
CITY="Greenwich"
STATE="OH"
ZIPCODE="44837"
PHONE="0000000000"
CURRENCY="USD"

CREDITCARDNUMBER="0000000000000000"  #Enter the number without any space
CARDTYPE="VISA" # Possible values for this are AMERICANEXPRESS or CARTASI or CARTEBLEUE or DANKORT 
				# or DISCOVER or DOMESTICMAESTRO or INTERNATIONALMAESTRO or JCB or MASTERCARD or
				# VISAELECTRON or VISA
EXPIRYMONTH="03" # Put a 0 in front if the month is less than 10, like 03 or 04
EXPIRYYEAR="2050"

#Don't change anything below this line

import requests
from threading import Thread
import Queue
import uuid
def addaddress(email,password):
	sess=requests.session()
	sess.headers.update({"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"})
	print "Logging in to {0}".format(email)
	if COUNTRY=="US":
		sess.cookies["CONSUMERCHOICE"]="us/en_us"
		sess.cookies["NIKE_COMMERCE_COUNTRY"]="US"
		sess.cookies["NIKE_COMMERCE_LANG_LOCALE"]="en_US"
		sess.cookies["nike_locale"]="us/en_US"
		e=sess.post("https://unite.nike.com/loginWithSetCookie?appVersion=287&experienceVersion=249&uxid=com.nike.commerce.snkrs.web&locale=en_US&backendEnvironment=identity&browser=Google%20Inc.&os=undefined&mobile=false&native=false",json={"username":email,"password":password,"keepMeLoggedIn":True,"client_id":"PbCREuPr3iaFANEDjtiEzXooFl7mXGQ7","ux_id":"com.nike.commerce.snkrs.web","grant_type":"password"})
	else:
		sess.cookies["CONSUMERCHOICE"]="gb/en_gb"
		sess.cookies["NIKE_COMMERCE_COUNTRY"]="GB"
		sess.cookies["NIKE_COMMERCE_LANG_LOCALE"]="en_GB"
		sess.cookies["nike_locale"]="gb/en_GB"
		e=sess.post("https://unite.nike.com/loginWithSetCookie?appVersion=287&experienceVersion=249&uxid=com.nike.commerce.snkrs.web&locale=en_GB&backendEnvironment=identity&browser=Google%20Inc.&os=undefined&mobile=false&native=false",json={"username":email,"password":password,"keepMeLoggedIn":True,"client_id":"PbCREuPr3iaFANEDjtiEzXooFl7mXGQ7","ux_id":"com.nike.commerce.snkrs.web","grant_type":"password"})
	e.raise_for_status()
	token=e.json()["access_token"]
	uid=str(uuid.uuid4())
	e=sess.get("https://paymentcc.nike.com/services/add?id="+uid)
	e=sess.post("https://paymentcc.nike.com/creditcardsubmit/"+uid+"/store",json={"accountNumber":CREDITCARDNUMBER,"cardType":CARDTYPE,"expirationMonth":EXPIRYMONTH,"expirationYear":EXPIRYYEAR,"creditCardInfoId":uid,"cvNumber":None})
	try:
		e.raise_for_status()
	except Exception as ee:
		print "Failed to store cc info"
		raise ee
	e=sess.post("https://api.nike.com/commerce/storedpayments/consumer/savepayment",json={"currency":"USD","isDefault":True,"billingAddress":{"address1":ADDRESSLINE1,"city":CITY,"country":COUNTRY,"firstName":FIRSTNAME,"lastName":LASTNAME,"phoneNumber":PHONE,"postalCode":ZIPCODE,"state":STATE},"creditCardInfoId":uid,"type":"CreditCard"},headers={"authorization":("Bearer "+token)})
	try:
		e.raise_for_status()
	except Exception as ee:
		print e.text
		raise ee
alls=open(ACCOUNTFILENAME,'r').read().split('\n')
alls=[p.strip().split(":",1) for p in alls if p.strip()!=""]
alls1=Queue.Queue()
for p in alls:
	alls1.put(p)
def f():
	while True:
		try:
			emp=alls1.get_nowait()
		except:
			return
		try:
			addaddress(emp[0],emp[1])
			print "Successfully added cc info for {0}".format(emp[0])
		except Exception as e:
			print e
			print "Error adding cc info to {0}".format(emp[0])
for i in range(0,20):
	Thread(target=f).start()
