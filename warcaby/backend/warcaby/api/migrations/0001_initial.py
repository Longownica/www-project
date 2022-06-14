# Generated by Django 4.0.5 on 2022-06-14 18:26

from django.db import migrations, models
import picklefield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CheckersGame',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('finished', models.BooleanField(default=False)),
                ('whites_turn', models.BooleanField(default=True)),
                ('white_won', models.BooleanField(default=False)),
                ('state', picklefield.fields.PickledObjectField(editable=False)),
            ],
        ),
    ]
