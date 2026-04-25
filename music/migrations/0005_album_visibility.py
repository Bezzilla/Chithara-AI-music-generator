from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0004_add_user_password_hash'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='visibility',
            field=models.CharField(
                choices=[('PUBLIC', 'Public'), ('PRIVATE', 'Private'), ('INVITE', 'Invite Only')],
                default='PRIVATE',
                max_length=10,
            ),
        ),
    ]
