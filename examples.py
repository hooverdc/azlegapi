from azlegapiclient import AzLegApiClient
from lxml import etree

import unittest

api = AzLegApiClient(username='DHoover', password='B23da@d8s')

# Take parameters str/int
# Return dicts

# print(api.sponsored_bills(121, 17))

# print(repr(api.session_by_id(121)))

# print(repr(api.sessions()))

# print(repr(api.bill_info(121,'HB2001')))

# print(api.bills_by_session_id(121))

print(api.committee_actions('H','S'))

print(api.floor_votes_by_bill(121,'SB1185'))