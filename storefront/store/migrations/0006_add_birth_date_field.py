# Generated by Django 4.0 on 2021-12-28 17:30


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_change_name_to_fit_datagrip'),
    ]

    operations = [
        migrations.AddField(
            model_name='Customer',
            name='birth_date',
            field=models.DateTimeField(auto_now_add=True)
        ),
    ]