from django.db import models
from django.utils import timezone
import json

class ScrapeHistory(models.Model):
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]
    
    url = models.URLField(max_length=500)
    title = models.CharField(max_length=500, blank=True)
    scraped_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    content_json = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-scraped_at']
        
    def __str__(self):
        return f"{self.url} - {self.status}"