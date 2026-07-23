from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Drive, EligibilityRule


def bump_drives_cache_version():
    """
    Incrementing a version number is cheaper and simpler than trying
    to enumerate and delete every affected student's cache key —
    old versioned keys just expire naturally via their TTL.
    """
    try:
        cache.incr('drives_cache_version')
    except ValueError:
        # Key doesn't exist yet (first run) — initialize it
        cache.set('drives_cache_version', 1, timeout=None)


@receiver(post_save, sender=Drive)
@receiver(post_delete, sender=Drive)
def invalidate_on_drive_change(sender, **kwargs):
    bump_drives_cache_version()


@receiver(post_save, sender=EligibilityRule)
@receiver(post_delete, sender=EligibilityRule)
def invalidate_on_rule_change(sender, **kwargs):
    bump_drives_cache_version()