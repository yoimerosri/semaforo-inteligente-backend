from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sensores', '0004_sensor_updated_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sensor',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
