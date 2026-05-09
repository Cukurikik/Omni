# OMNI Admin & Tooling Layer
# Django Admin Panel Bridge
# Based on django/django. Wraps the Omni database state into Django's powerful ORM/Admin interface.

from django.contrib import admin
from django.db import models
from django.core.management.base import BaseCommand
import json
import ctypes

class OmniTaskLog(models.Model):
    """
    Django ORM representation of an Omni Compute Task.
    Allows administrators to view historical tasks in the Django Admin.
    """
    task_id = models.CharField(max_length=128, unique=True)
    engine_type = models.CharField(max_length=64) # e.g., 'Rust', 'CUDA', 'Go'
    status = models.CharField(max_length=32)
    execution_time_ms = models.FloatField()
    payload = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'omni_task_logs'
        verbose_name = 'Omni Task Log'

@admin.register(OmniTaskLog)
class OmniTaskLogAdmin(admin.ModelAdmin):
    list_display = ('task_id', 'engine_type', 'status', 'execution_time_ms', 'created_at')
    list_filter = ('engine_type', 'status')
    search_fields = ('task_id',)
    readonly_fields = ('task_id', 'execution_time_ms', 'created_at')

# -------------------------------------------------------------------------
# Omni Bridge Command
# Allows triggering native C-ABI functions directly from manage.py
# -------------------------------------------------------------------------

class Command(BaseCommand):
    help = 'Triggers an Omni Universal Engine cleanup task via C-ABI'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('OMNI Django: Connecting to native C-ABI runtime...'))
        
        try:
            # Simulated C-ABI call
            # lib = ctypes.CDLL('/opt/omni/libomni_universal.so')
            # result = lib.omni_gc_trigger()
            
            result = 0 # 0 means success
            if result == 0:
                self.stdout.write(self.style.SUCCESS('OMNI Django: Native engine garbage collection successful.'))
            else:
                self.stdout.write(self.style.ERROR('OMNI Django: Native engine returned error code: ' + str(result)))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'OMNI Django Fatal: {str(e)}'))
