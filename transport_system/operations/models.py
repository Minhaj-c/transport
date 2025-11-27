"""
Operations and Analytics Models
Tracks performance metrics and financial data
"""

from django.db import models
from django.conf import settings
from schedules.models import Bus
from routes.models import Route
from decimal import Decimal


class WeeklyPerformance(models.Model):
    """
    Weekly Performance Model
    Tracks operational and financial performance per route per bus
    """
    # Relationships
    bus = models.ForeignKey(
        Bus,
        on_delete=models.CASCADE,
        related_name='weekly_performances',
        help_text="Bus being tracked"
    )
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name='weekly_performances',
        help_text="Route being served"
    )
    
    # Time period
    week_start_date = models.DateField(
        help_text="Start date (Monday) of the week being recorded"
    )
    
    # Passenger tracking
    estimated_passengers = models.PositiveIntegerField(
        default=0,
        help_text="Estimated passengers from PreInform data (auto-calculated)"
    )
    actual_passengers = models.PositiveIntegerField(
        default=0,
        help_text="Actual passengers from ticket sales (manually entered)"
    )
    total_passengers = models.PositiveIntegerField(
        help_text="Total passengers (estimated + actual, auto-calculated)"
    )
    
    # Distance tracking
    total_kms = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total kilometers traveled this week"
    )
    
    # Financial metrics (auto-calculated)
    total_revenue = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        editable=False,
        help_text="Total revenue earned (auto-calculated)"
    )
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        editable=False,
        help_text="Total operational cost (auto-calculated)"
    )
    total_profit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        editable=False,
        help_text="Net profit (revenue - cost, auto-calculated)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Weekly Performance'
        verbose_name_plural = 'Weekly Performances'
        ordering = ['-week_start_date', 'bus']
        unique_together = ['bus', 'route', 'week_start_date']
        indexes = [
            models.Index(fields=['week_start_date']),
            models.Index(fields=['bus', 'week_start_date']),
            models.Index(fields=['route', 'week_start_date']),
        ]
    
    def __str__(self):
        return f"{self.bus} - {self.route} - Week of {self.week_start_date}"
    
    def save(self, *args, **kwargs):
        """
        Override save to auto-calculate financial metrics
        """
        # Auto-calculate total passengers
        self.total_passengers = self.estimated_passengers + self.actual_passengers
        
        # Use actual passengers for revenue if available, otherwise estimated
        passengers_for_revenue = (
            self.actual_passengers if self.actual_passengers > 0 
            else self.estimated_passengers
        )
        
        # Calculate revenue
        # Assumption: Average journey is half the route distance
        average_journey_distance = self.route.total_distance * Decimal('0.5')
        self.total_revenue = (
            passengers_for_revenue * 
            average_journey_distance * 
            Decimal(settings.TICKET_PRICE_PER_KM)
        )
        
        # Calculate cost (fuel cost only for now)
        fuel_used = self.total_kms / Decimal(self.bus.mileage)
        self.total_cost = fuel_used * Decimal(settings.FUEL_PRICE_PER_LITER)
        
        # Calculate profit
        self.total_profit = self.total_revenue - self.total_cost
        
        super().save(*args, **kwargs)
    
    def profit_per_km(self):
        """Calculate profit per kilometer"""
        if self.total_kms > 0:
            return round(self.total_profit / self.total_kms, 2)
        return 0
    
    def revenue_per_passenger(self):
        """Calculate average revenue per passenger"""
        if self.total_passengers > 0:
            return round(self.total_revenue / self.total_passengers, 2)
        return 0
    
    def is_profitable(self):
        """Check if this operation was profitable"""
        return self.total_profit > 0