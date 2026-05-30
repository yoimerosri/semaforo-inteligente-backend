from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('sensores', '0003_sensor_confidence_sensor_vehicle_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='sensor',
            name='updated_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
