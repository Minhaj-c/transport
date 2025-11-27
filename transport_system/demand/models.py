"""
Demand Alert Model
Allows passengers to report crowd/demand at bus stops
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from routes.models import Stop


class DemandAlert(models.Model):
    """
    Demand Alert Model
    Passengers can report when many people are waiting at a stop
    Helps company dispatch buses quickly to high-demand locations
    """
    # User reporting the demand
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='demand_alerts',
        help_text="Passenger reporting the crowd"
    )
    
    # Location
    stop = models.ForeignKey(
        Stop,
        on_delete=models.CASCADE,
        related_name='demand_alerts',
        help_text="Stop where people are waiting"
    )
    
    # Demand details
    number_of_people = models.PositiveIntegerField(
        help_text="Approximate number of people waiting (including reporter)"
    )
    
    # Status tracking
    STATUS_CHOICES = (
        ('reported', 'Reported'),
        ('verified', 'Verified by Admin'),
        ('dispatched', 'Bus Dispatched'),
        ('resolved', 'Resolved'),
        ('expired', 'Expired'),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='reported',
        help_text="Current status of alert"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When alert was created"
    )
    expires_at = models.DateTimeField(
        help_text="When this alert expires (1 hour from creation)"
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When alert was resolved"
    )
    
    # Admin notes
    admin_notes = models.TextField(
        blank=True,
        help_text="Notes from control room"
    )
    
    class Meta:
        verbose_name = 'Demand Alert'
        verbose_name_plural = 'Demand Alerts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at', 'status']),
            models.Index(fields=['stop', 'status']),
        ]
    
    def save(self, *args, **kwargs):
        """
        Override save to automatically set expiry time
        """
        if not self.pk:  # If creating new alert
            self.expires_at = timezone.now() + timezone.timedelta(hours=1)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.email}: {self.number_of_people} people at {self.stop.name}"
    
    def is_active(self):
        """Check if alert is still valid (not expired)"""
        return timezone.now() < self.expires_at and self.status not in ['resolved', 'expired']
    
    def mark_resolved(self):
        """Mark alert as resolved"""
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.save()
    
    def mark_expired(self):
        """Mark alert as expired"""
        self.status = 'expired'
        self.save()