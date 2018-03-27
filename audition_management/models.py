from django.db import models
from django.contrib.auth.models import User


class AuditionAccount(models.Model):
    GENDER_CHOICES = (
        (0, "Female"),
        (1, "Male")
    )
    ETHNICITY_CHOICES = (
        (0, "Asian"),
        (1, "Black"),
        (2, "Hispanic"),
        (3, "Native American"),
        (4, "White")
    )

    profile = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='audition_account',
        blank=True,
        null=True,
    )
    gender = models.IntegerField("gender", choices=GENDER_CHOICES, blank=True, null=True)
    age = models.IntegerField("age", blank=True, null=True)
    ethnicity = models.IntegerField("ethnicity", choices=ETHNICITY_CHOICES, blank=True, null=True)
    location = models.CharField("location", max_length=512, blank=True, null=True)

    def __str__(self):
        return "%s %s" % (self.profile.first_name, self.profile.last_name)

    def as_dict(self):
        tags = self.tags.all()
        tags = [str(obj) for obj in tags]
        return {
            "user_pk": self.profile.id,
            "name": '"' + str(self) + '"',
            "email": '"' + self.profile.email + '"',
            "tags": tags,
        }


class CastingAccount(models.Model):
    profile = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='casting_account',
        blank=True,
        null=True,
    )

    def __str__(self):
        return "%s %s" % (self.profile.first_name, self.profile.last_name)


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
    status = models.IntegerField("Status", choices=STATUS_CHOICES, default=1)

    def __str__(self):              # __unicode__ on Python 2
        return "%s, %s" % (self.name, self.description)

    def as_dict(self):
        events = PerformanceEvent.objects.filter(role=self)
        events = [obj.as_dict() for obj in events]
        tags = Tag.objects.filter(role=self)
        tags = [str(obj) for obj in tags]
        return {
            "role": {
                "id": self.pk,
                "name": '"' + self.name + '"',
                "description": '"' + self.description + '"',
                "domain": self.domain,
                "address": self.studio_address,
                "agent": str(self.agent),
                "agent_id": self.agent.id,
                "user_pk": self.agent.profile.id,
            },
            "events": events,
            "tags": tags,
        }


class PerformanceEvent(models.Model):
    date = models.DateTimeField("Date")
    name = models.CharField("Name", max_length=128)
    role = models.ForeignKey(Role, on_delete=models.CASCADE,
                             related_name="dates")

    def __str__(self):              # __unicode__ on Python 2
        return "%s %s" % (self.date, self.name)

    def as_dict(self):
        return {
            "event": {
                "date": '"' + str(self.date) + '"',
                "name": '"' + self.name + '"'
            },
        }


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

    def __str__(self):
        return self.name


class Application(models.Model):
    user = models.ForeignKey(
        AuditionAccount,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    posting = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="applications",
    )

    def as_dict(self):
        return {
            "user": self.user.as_dict(),
            "id": self.pk,
        }


class PastWork(models.Model):
    name = models.CharField("Description of Past Works", max_length=128)
    account = models.ForeignKey(
        AuditionAccount,
        on_delete=models.CASCADE,
        related_name="pastworks",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name


class Alert(models.Model):
    text = models.CharField("Alert Text", max_length=256)
    account = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="messages",
    )
