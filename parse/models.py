from django.db import models
from django.utils.translation import ugettext_lazy as _

class RelayEntry(models.Model):
    timestamp = models.DateTimeField()
    uid = models.CharField(_('UID'), max_length=32)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    data = models.PositiveIntegerField(_('Data'))
    client_ip = models.IPAddressField(_('Client IP'))
    client_port = models.PositiveIntegerField()
    device_ip = models.IPAddressField(_('Device IP'))
    device_port = models.PositiveIntegerField()
    end_reason = models.SmallIntegerField()

    def __unicode__(self):
        return '%s - %s' % (self.uid, str(self.start_time))

class RelaySession(models.Model):
    uid = models.CharField(_('UID'), max_length=32)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)
    relay_entry = models.ForeignKey('RelayEntry', null=True, blank=True)

    def __unicode__(self):
        if self.start_time:
            return '%s (%s)' % (self.uid, self.start_time)
        else:
            return '%s (%s)' % (self.uid, 'Active' if self.active else 'Archived')
