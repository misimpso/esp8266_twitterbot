from actions import Actions
from credentials import accounts

for name in accounts:
    accounts[name] = Actions(**accounts[name])

accounts["test"].tweet("Hello Ladies + Gentlemen, a signed OAuth request!")


