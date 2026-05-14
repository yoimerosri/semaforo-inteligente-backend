from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('semaforo', '0002_alter_intersection_options_alter_road_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='trafficlight',
            name='green_duration',
            field=models.PositiveSmallIntegerField(default=5),
        ),
    ]
