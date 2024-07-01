# Generated by Django 4.2.8 on 2024-06-30 21:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('nombre', models.CharField(max_length=100)),
                ('ubicacion', models.CharField(max_length=100)),
                ('estado', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Sensor',
                'verbose_name_plural': 'Sensores',
                'unique_together': {('nombre', 'ubicacion')},
            },
        ),
        migrations.CreateModel(
            name='Reservacion',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('fecha_reservacion', models.DateTimeField()),
                ('active', models.BooleanField(default=True)),
                ('sensor_activado', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='reservation.sensor')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Reservacion',
                'verbose_name_plural': 'Reservaciones',
                'unique_together': {('fecha_reservacion',)},
            },
        ),
    ]
