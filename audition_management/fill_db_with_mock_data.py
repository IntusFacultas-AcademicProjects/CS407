from audition_management.models import CastingAccount, AuditionAccount, Role

descrs = [
    'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc pulvinar urna sed dui auctor maximus quis nec orci.',
    'Integer congue nibh mattis purus viverra, nec euismod mi congue.',
    'Nunc auctor ipsum id erat laoreet euismod.',
    'Donec rutrum mauris in nisi cursus, at sagittis erat rhoncus.',
    'Vestibulum at bibendum risus, quis consectetur dui. Donec finibus risus eget nibh congue suscipit.'
]

addrs = [
    '320 s grant st',
    '1600 pennsylvania av',
    '140 new montgomery st',
    '1600 Ampetheatre av'
]

for i in range(0, 100):
    Role.objects.create(
        name='Test Role # {}'.format(i),
        description=descrs[i % len(descrs)],
        domain=Role.DOMAIN_CHOICES[i % len(Role.DOMAIN_CHOICES)],
        studio_address=addrs[i % len(addrs)],
        agent=CastingAccount.objects.all()[0],
        status=i % 2
    )