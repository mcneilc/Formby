import datetime

from main.models import *

for round in ('East End', 'West End', 'Ochtrelure'):
    Round.objects.get_or_create(name=round)

for customer in ("Craig's ma", "My ma"):
    Customer.objects.get_or_create(
        name=customer,
        defaults={
            'number_name_of_house': 2,
            'address1': 'Dalrymple Terrace',
            'postcode': 'DG9 8DH',
            'phone': '01776 706854',
            'email': 'bob@example.com'}
        )

for round, customer in zip(Round.objects.all(),
                           Customer.objects.all()):
    JobSchedule.objects.get_or_create(
        round=round,
        customer=customer,
        defaults={
            'cost': 10,
            'start_date': datetime.date.today(),
            'frequency': 4,
            }
        )
