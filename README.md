Facebook 6 handshake rule tester. Scrapy/Selenium based.

Parses friendlists of 2 users from input, parses their friendlists until it finds a chain, after which returns depth of chain and the chain's links as a string.

Requirements: 
- MongoDB listening at Localhost, 27017
- Facebook login (FB_LOGIN) and password (FB_PWD) in a .env file at project root.


Running:
python runner.py -u <username_1>,<username_2>
