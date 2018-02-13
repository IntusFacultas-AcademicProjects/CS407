from audition_management.models import CastingAccount, Role, Tag
from random import randint

descriptions = [
    'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc pulvinar urna sed dui auctor maximus quis nec orci.',
    'Integer congue nibh mattis purus viverra, nec euismod mi congue.',
    'Nunc auctor ipsum id erat laoreet euismod.',
    'Donec rutrum mauris in nisi cursus, at sagittis erat rhoncus.',
    'Vestibulum at bibendum risus, quis consectetur dui. Donec finibus risus eget nibh congue suscipit.'
]

addresses = [
    '320 s grant st',
    '1600 pennsylvania av',
    '140 new montgomery st',
    '1600 Ampetheatre av'
]

tags = [
    'Male',
    'Female',
    'High pitched voice',
    'Low pitched voice',
    'Fast',
    'Slow',
    'Quick',
    'Taggy',
    'Good',
    'Amazing'
]

tag_index = 0
for i in range(0, 100):
    role = Role.objects.create(
        name='Test Role # {}'.format(i),
        description=descriptions[i % len(descriptions)],
        domain=Role.DOMAIN_CHOICES[i % len(Role.DOMAIN_CHOICES)],
        studio_address=addresses[i % len(addresses)],
        agent=CastingAccount.objects.all()[0],
        status=i % 2
    )

    for _ in range(0, randint(3, 10)):
        Tag.objects.create(
            name=tags[tag_index],
            role=role,
            agent=CastingAccount.objects.all()[0]
        )
        tag_index += 1
        if tag_index >= len(tags):
            tag_index = 0
