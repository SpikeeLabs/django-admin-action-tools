# Generated by Django 3.0.10 on 2020-10-31 20:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("market", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Inventory",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.PositiveIntegerField()),
                (
                    "item",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="market.Item"),
                ),
            ],
            options={
                "ordering": ["shop", "item__name"],
            },
        ),
        migrations.CreateModel(
            name="Shop",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=120)),
            ],
        ),
        migrations.DeleteModel(
            name="Stock",
        ),
        migrations.AddField(
            model_name="inventory",
            name="shop",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="inventory",
                to="market.Shop",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="inventory",
            unique_together={("shop", "item")},
        ),
    ]
