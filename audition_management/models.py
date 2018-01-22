from django.db import models
from django.contrib.auth.models import User


class AuditionAccount(models.Model):
    profile = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='audition_account',
        blank=True,
        null=True,
    )


class CastingAccount(models.Model):
    profile = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='casting_account',
        blank=True,
        null=True,
    )

# Create your models here.


class Role(models.Model):
    DOMAIN_CHOICES = (
        (0, "General Acting"),
        (1, "Voice Acting"),
        (2, "Stage Acting"),
        (3, "Special Effects"),
        (4, "Stage Crew"),
        (5, "Other"),
    )
    STATUS_CHOICES = (
        (0, "Closed"),
        (1, "Open"),
    )
    name = models.CharField("Name", max_length=256)
    description = models.CharField("description", max_length=512)
    domain = models.IntegerField("Role", choices=DOMAIN_CHOICES)
    studio_address = models.CharField("Studio Address", max_length=512)
    agent = models.ForeignKey(CastingAccount, on_delete=models.CASCADE,
                              related_name="roles")
    domain = models.IntegerField("Status", choices=STATUS_CHOICES)


class PerformanceEvent(models.Model):
    date = models.DateField("Date")
    name = models.CharField("Name", max_length=128)
    role = models.ForeignKey(Role, on_delete=models.CASCADE,
                             related_name="dates")


class Tag(models.Model):
    name = models.CharField("Name", max_length=128)
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="tags",
        blank=True,
        null=True,
    )
    account = models.ForeignKey(
        AuditionAccount,
        on_delete=models.CASCADE,
        related_name="tags",
        blank=True,
        null=True,
    )
