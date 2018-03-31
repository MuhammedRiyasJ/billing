from __future__ import unicode_literals

from django.db import models
from app.models import BaseModel

CHOICE =(('admin', 'Admin'),('staff', 'Staff'),)


# Create your models here.

class Profile(BaseModel):
	user = models.ForeignKey("auth.User",limit_choices_to={'is_active':True})
	user_type = models.CharField(max_length=6,choices=CHOICE)
	shops = models.ManyToManyField("shops.Shop",related_name='user_shops',blank=True,limit_choices_to={'is_deleted':False})
	current_shop = models.ForeignKey("shops.Shop",related_name='current_shop',limit_choices_to={'is_deleted':False})
	tax_only = models.BooleanField(default=False)

	is_deleted = models.BooleanField(default=False)

	class Meta:
		db_table = 'user_profile'
		verbose_name = 'user_profile'
		verbose_name_plural = 'user_profiles'
		ordering = ('user',)

	def __unicode__(self):
		return self.name





