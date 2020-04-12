from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import datetime, timedelta
from pytz import utc


class CoolerSensor(models.Model):
    """
    write by API Gateway
    read by controller
    """
    created = models.DateTimeField(auto_now_add=True, primary_key=True)
    air_in_temperature = models.FloatField(null=True, blank=True)
    air_out_temperature = models.FloatField(null=True, blank=True)

    air_in_humidity = models.FloatField(null=True, blank=True)
    air_out_humidity = models.FloatField(null=True, blank=True)

    heater_temperature = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        keep only 30 000 latest values
        :param args:
        :param kwargs:
        :return:
        """

        if CoolerSensor.objects.all().count() >= 30000:
            CoolerSensor.objects.all().order_by('created')[0].delete()
        super(CoolerSensor, self).save(*args, **kwargs)

    @classmethod
    def get_status(cls):
        """
        get latest values
        :return:
        """
        try:
            return cls.objects.filter(
                created__gte=utc.localize(
                    datetime.now() - timedelta(seconds=5)
                )
            ).order_by('-created')[0]
        except IndexError:
            return None
        except cls.ObjectDoesNotExist:
            return None


class Cooler(models.Model):
    """
    write by controller
    read by api gateway
    """
    created = models.DateTimeField(auto_now_add=True, primary_key=True)
    temperature_in = models.FloatField(null=True, blank=True)
    humidity_in = models.FloatField(null=True, blank=True)

    temperature_level_max = models.FloatField(null=True, blank=True)
    temperature_level_min = models.FloatField(null=True, blank=True)

    humidity_level_max = models.FloatField(null=True, blank=True)
    humidity_level_min = models.FloatField(null=True, blank=True)

    power_temperature = models.SmallIntegerField(
        null=True,
        blank=True,
        validators=[
            MaxValueValidator(1),
            MinValueValidator(0)
        ]
    )

    power_humidity = models.SmallIntegerField(
        null=False,
        blank=False,
        validators=[
            MaxValueValidator(1),
            MinValueValidator(0)
        ]
    )

    class Meta:
        ordering = ['-created']