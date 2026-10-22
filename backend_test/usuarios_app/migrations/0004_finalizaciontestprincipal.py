from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
        ('usuarios_app', '0003_pregunta_nuevo_tipo_test_test_editable_opcion_nuevo_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinalizacionTestPrincipal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('test_principal', models.CharField(choices=[('DAT', 'DAT'), ('IPP', 'IPP'), ('HSPQ', 'HSPQ')], max_length=10)),
                ('fecha_finalizacion', models.DateTimeField(auto_now_add=True)),
                ('estudiante', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usuarios.user')),
            ],
            options={
                'db_table': 'finalizacion_test_principal',
                'constraints': [models.UniqueConstraint(fields=('estudiante', 'test_principal'), name='uniq_finalizacion_estudiante_test')],
            },
        ),
    ]
