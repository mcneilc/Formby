import datetime

from django.db import models


class Round(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class Customer(models.Model):
    name = models.CharField(max_length=150)
    number_name_of_house = models.CharField(max_length=150)
    address1 = models.CharField(max_length=150)
    address2 = models.CharField(max_length=150, blank=True)
    postcode = models.CharField(max_length=10)
    phone = models.CharField(max_length=12)
    email = models.EmailField()

    @property
    def address(self):
        return (u'{number_name_of_house} '
                '{address1} {address2}, {postcode}'
                .format(**self.__dict__))


class JobSchedule(models.Model):
    round = models.ForeignKey(Round, related_name="job_schedules")
    customer = models.ForeignKey(Customer)
    cost = models.IntegerField()
    start_date = models.DateField()
    frequency = models.IntegerField()

    def get_next_due_date(self, last_job):
        return last_job.date + datetime.timedelta(weeks=self.frequency)

    def current_debt(self):
        return self.jobs.filter(paid_on__isnull=True).count() * self.cost
        
    def save(self, *args, **kwargs):
        create_job = self.pk is None
        super(JobSchedule, self).save(*args, **kwargs)
        if create_job:
            Job.objects.create(schedule=self, date=self.start_date)


class Job(models.Model):
    schedule = models.ForeignKey(JobSchedule, related_name="jobs")
    date = models.DateField()
    completed_on = models.DateField(null=True, blank=True)
    paid_on = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.create_new_job_if_self_is_completed()
        super(Job, self).save(*args, **kwargs)

    def create_new_job_if_self_is_completed(self):
        if self.pk:
            saved_self = Job.objects.get(pk=self.pk)
            if not saved_self.completed_on and self.completed_on:
                Job.objects.create(
                    schedule=self.schedule,
                    date=self.schedule.get_next_due_date(self)
                    )
