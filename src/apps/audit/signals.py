import logging

from django.forms.models import model_to_dict

logger = logging.getLogger("business")

SENSITIVE_FIELDS = {'password', 'token', 'secret', 'key', 'api_key', 'access_token', 'refresh_token'}

def get_model_snapshot(instance):
    """Convert model instance to a dictionary, masking sensitive fields."""
    try:
        data = model_to_dict(instance)
        for field in SENSITIVE_FIELDS:
            if field in data:
                data[field] = "********"
        return data
    except Exception as e:
        logger.warning(f"Failed to create snapshot for {instance.__class__.__name__}: {e}")
        return {}

def get_diff(before, after):
    """Calculate the difference between two snapshots."""
    changes = {}
    if not before:
        return {k: {"old": None, "new": v} for k, v in after.items()}
    if not after:
        return {k: {"old": v, "new": None} for k, v in before.items()}
        
    all_keys = set(before.keys()) | set(after.keys())
    for key in all_keys:
        old_val = before.get(key)
        new_val = after.get(key)
        if old_val != new_val:
            changes[key] = {"old": old_val, "new": new_val}
    return changes

class AuditManager:
    @staticmethod
    def handle_pre_save(sender, instance, **kwargs):
        if hasattr(instance, '_audit_skip'):
            return
            
        if instance.pk:
            try:
                old_instance = sender.objects.filter(pk=instance.pk).first()
                instance._audit_before = get_model_snapshot(old_instance) if old_instance else None
            except Exception:
                instance._audit_before = None
        else:
            instance._audit_before = None

    @staticmethod
    def handle_post_save(sender, instance, created, **kwargs):
        if hasattr(instance, '_audit_skip'):
            return

        action = 'CREATE' if created else 'UPDATE'
        before = getattr(instance, '_audit_before', None)
        after = get_model_snapshot(instance)
        
        if action == 'UPDATE':
            changes = get_diff(before, after)
            if not changes:
                return
        else:
            changes = get_diff(None, after)
        
        AuditManager._log_event(action, sender, instance, before, after, changes)

    @staticmethod
    def handle_pre_delete(sender, instance, **kwargs):
        if hasattr(instance, '_audit_skip'):
            return
        
        before = get_model_snapshot(instance)
        AuditManager._log_event('DELETE', sender, instance, before, None, get_diff(before, None))

    @staticmethod
    def _log_event(action, sender, instance, before, after, changes):
        model_name = sender.__name__
        object_id = str(instance.pk)

        log_data = {
            "event": f"audit_{model_name.lower()}_{action.lower()}",
            "action": action,
            "model": model_name,
            "object_id": object_id,
            "before": before,
            "after": after,
            "changes": changes,
        }
        logger.info(f"{action} {model_name} {object_id}", extra={"extra_data": log_data})

        # A auditoria é persistida exclusivamente em arquivo via logger "business".

def register_audit_signals(model):
    from django.db.models.signals import post_save, pre_delete, pre_save
    pre_save.connect(AuditManager.handle_pre_save, sender=model)
    post_save.connect(AuditManager.handle_post_save, sender=model)
    pre_delete.connect(AuditManager.handle_pre_delete, sender=model)
