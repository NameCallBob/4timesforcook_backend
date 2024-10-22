# Generated by Django 5.0.2 on 2024-03-19 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Recipe_At',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rid', models.CharField(max_length=50)),
                ('minutes', models.IntegerField()),
                ('nutrition', models.TextField()),
                ('n_steps', models.IntegerField()),
                ('n_ingredients', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Recipe_Ob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rid', models.CharField(max_length=50)),
                ('name', models.TextField()),
                ('tags', models.TextField()),
                ('steps', models.TextField()),
                ('description', models.TextField()),
                ('ingredients', models.TextField()),
            ],
        ),
    ]
# Generated by Django 5.0.2 on 2024-03-19 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Recipe_At',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rid', models.CharField(max_length=50)),
                ('minutes', models.IntegerField()),
                ('nutrition', models.TextField()),
                ('n_steps', models.IntegerField()),
                ('n_ingredients', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Recipe_Ob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rid', models.CharField(max_length=50)),
                ('name', models.TextField()),
                ('tags', models.TextField()),
                ('steps', models.TextField()),
                ('description', models.TextField()),
                ('ingredients', models.TextField()),
            ],
        ),
    ]
