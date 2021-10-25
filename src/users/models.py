from django.conf import settings
from django.contrib.auth.models import Group, User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from base.models import BaseModel


class Employee(BaseModel):
    employee_id = models.CharField(max_length=255, unique=True)
    user = models.OneToOneField(User, on_delete=models.RESTRICT, related_name='employee')

    class Meta:
        db_table = 'employee'
        verbose_name_plural = 'Employees'
        verbose_name = 'Employee'
        # ordering = ['-id']

    def __str__(self):
        return "{} {}".format(self.employee_id, self.user)


@receiver(post_save, sender=Employee)
def assign_default_group_employee(sender, instance: Employee, created, **kwargs):
    if created:
        instance.user.groups.add(Group.objects.get(name=settings.EMPLOYEE))
