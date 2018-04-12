import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from audition_management.models import CastingAccount, AuditionAccount, Message
from random import randint
from datetime import datetime

MESSAGES_TO_CREATE = 10

messages = [
	'Hey man how are you doing?',
	'I am doing well and you?',
	'We should get lunch soon!',
	'It would be great to see you',
]

accounts = [
	CastingAccount.objects.all()[0],
	AuditionAccount.objects.all()[0]
]

for i in range(0, MESSAGES_TO_CREATE):
	message = Message.objects.create(
		sender=accounts[i % len(accounts)].profile,
		receiver=accounts[(i+1) % len(accounts)].profile,
		timestamp=datetime.now(),
		text=messages[i % len(messages)]
	)