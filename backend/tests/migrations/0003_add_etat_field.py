# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0002_alter_test_total_questions_alter_test_version_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='etat',
            field=models.CharField(
                choices=[('test_initial', 'Test initial'), ('test_final', 'Test final')],
                default='test_final',
                help_text='Détermine si c\'est un test initial ou final',
                max_length=20,
                verbose_name='État'
            ),
        ),
        migrations.AddField(
            model_name='testattempt',
            name='etat',
            field=models.CharField(
                choices=[('test_initial', 'Test initial'), ('test_final', 'Test final')],
                default='test_final',
                help_text='État du test (initial ou final)',
                max_length=20,
                verbose_name='État'
            ),
        ),
        migrations.AddIndex(
            model_name='test',
            index=models.Index(fields=['etat'], name='tests_test_etat_idx'),
        ),
        migrations.AddIndex(
            model_name='testattempt',
            index=models.Index(fields=['etat'], name='tests_testat_etat_idx'),
        ),
    ]

