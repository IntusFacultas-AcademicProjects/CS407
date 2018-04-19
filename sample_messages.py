import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from audition_management.models import CastingAccount, AuditionAccount, Message
from random import randint
from datetime import datetime

MESSAGES_TO_CREATE = 10

messages1 = [
	'Hey man how are you doing?',
	'I am doing well and you?',
	'We should get lunch soon!',
	'It would be great to see you',
]

messages2 = [
	'I have not seen you in forever!',
	'You are right, it has been too long',
	'Maybe sometime we can see a movie',
	'That would be really great!'
]

messages3 = [
	'Did you see that ludicrous display last night?',
	'What was Wenger thinking sending Walcott on that early?',
	'The thing about Arsenal is, they always try and walk it in!',
	'Yeah that is true'
]

messages4 = [
	'I cannot believe the white sox are this bad',
	'I mean I can, it is only year two of the rebuild',
	'Yeah but still, the pitching has been awful',
	'That we can agree on'
]

messages5 = [
	'I think Christopher Nolan is the best director of all time',
	'That is a ridiculous statement, he does not have a big enough body of work yet',
	'Well who would you say is the best director of all time',
	'Probably Steven Spielberg',
]

messages6 = [
	'What did you think of the Last Jedi?',
	'I did not like it much, it was the worst Star Wars movie yet',
	'Really? There were parts I did not like but overall I thought it was good',
	'Can we atleast agree that Rose was stupid',
	'Agreed'
]

accounts = [
	AuditionAccount.objects.all()[1],
	AuditionAccount.objects.all()[2]
]

for i in range(0, MESSAGES_TO_CREATE):
	message = Message.objects.create(
		sender=accounts[i % len(accounts)].profile,
		receiver=accounts[(i+1) % len(accounts)].profile,
		timestamp=datetime.now(),
		text=messages6[i % len(messages6)]
	)