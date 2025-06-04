from django.db import migrations

def create_loyalty_tiers(apps, schema_editor):
    LoyaltyTier = apps.get_model('movie', 'LoyaltyTier')
    
    # Create the tiers
    tiers = [
        {'name': 'bronze', 'points_required': 1500, 'discount_percentage': 3},
        {'name': 'silver', 'points_required': 3000, 'discount_percentage': 5},
        {'name': 'gold', 'points_required': 5000, 'discount_percentage': 7},
    ]
    
    for tier_data in tiers:
        LoyaltyTier.objects.create(**tier_data)

def remove_loyalty_tiers(apps, schema_editor):
    LoyaltyTier = apps.get_model('movie', 'LoyaltyTier')
    LoyaltyTier.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('movie', '0003_cinemahall_remove_movie_subscription_required_and_more'),
    ]

    operations = [
        migrations.RunPython(create_loyalty_tiers, remove_loyalty_tiers),
    ] 