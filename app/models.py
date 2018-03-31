from __future__ import unicode_literals
from django.db import models
import uuid
from django.utils.translation import ugettext_lazy as _

STATE_UT_CODE =(('01',' Jammu & Kashmir'),('02','Himachal Pradesh'),('03','Punjab'),('04','Chandigarh'),('05','Uttranchal'),
    ('06','Haryana'),('07','Delhi'),('08','Rajasthan'),('09','Uttar Pradesh'),('10','Bihar'),('11','Sikkim'),
    ('12','Arunachal Pradesh'),('13','Nagaland'),('14','Manipur'),('15','Mizoram'),('16','Tripura'),('17','Meghalaya'),
    ('18','Assam'),('19','West Bengal'),('20','Jharkhand'),('21','Odisha'),('22','Chhattisgarh'),('23','Madhya Pradesh'),
    ('24','Gujarat'),('25','Daman & Diu'),('26','Dadra & Nagar Haveli'),('27','Maharashtra'),('28','Andhra Pradesh'),
    ('29','Karnataka'),('30','Goa'),('31',' Lakshdweep'),('32','Kerala'),('33','Tamil Nadu'),('34','Pondicherry'),
    ('35','Andaman & Nicobar Islands'),('36','Telangana'),('37','Andra Pradesh'))

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creator = models.ForeignKey("auth.User",blank=True,related_name="creator_%(class)s_objects")
    updater = models.ForeignKey("auth.User",blank=True,related_name="updater_%(class)s_objects")
    date_added = models.DateTimeField(auto_now_add=True)    
    date_updated = models.DateTimeField(auto_now_add=True)  

    class Meta:
        abstract = True


class Notification(models.Model):
    shop = models.ForeignKey("shops.Shop",blank=True)
    message = models.TextField(blank=True,null=True)

    is_read = models.BooleanField(default=False)
    is_cheque = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    time = models.DateTimeField(auto_now_add=True)    
    
    class Meta:
        db_table = 'notification'
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
        ordering = ('-time',)  
    
    class Admin:
        list_display = ('message',)
    