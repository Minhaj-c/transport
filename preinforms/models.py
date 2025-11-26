"""
PreInform Model
Allows passengers to inform their travel plans in advance
"""

from django.db import models
from django.conf import settings
from routes.models import Route, Stop


class PreInform(models.Model):
    """
    PreInform Model
    Passengers can submit their travel plans in advance
    This helps company predict demand and plan operations
    """
    # User who is submitting the travel plan
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='preinforms',
        help_text="Passenger submitting the pre-inform"
    )
    
    # Route details
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name='preinforms',
        help_text="Route passenger intends to take"
    )
    
    # Travel details
    date_of_travel = models.DateField(
        help_text="Date passenger plans to travel"
    )
    desired_time = models.TimeField(
        help_text="Preferred boarding time"
    )
    
    # Boarding location
    boarding_stop = models.ForeignKey(
        Stop,
        on_delete=models.CASCADE,
        related_name='boarding_passengers',
        help_text="Stop where passenger will board"
    )
    
    # Number of passengers
    passenger_count = models.PositiveIntegerField(
        default=1,
        help_text="Number of passengers traveling"
    )
    
    # Status tracking
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('noted', 'Noted by Controller'),
        ('completed', 'Journey Completed'),
        ('cancelled', 'Cancelled'),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of pre-inform"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When pre-inform was submitted"
    )
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Pre-Inform'
        verbose_name_plural = 'Pre-Informs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['date_of_travel', 'route']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.user.email} on {self.date_of_travel} at {self.desired_time} (Route {self.route.number})"
    
    def is_active(self):
        """Check if pre-inform is still active"""
        from django.utils import timezone
        return self.date_of_travel >= timezone.now().date() and self.status == 'pending'