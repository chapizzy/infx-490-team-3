from django.db import models
from django.contrib.auth.models import User  # for user_id foreign key

class Produce(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Image(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('analyzed', 'Analyzed'),
    ]

    produce = models.ForeignKey(Produce, on_delete=models.CASCADE, related_name='images')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    image_path = models.ImageField(upload_to='produce_images/')
    upload_timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"Image {self.id} - {self.produce.name}"


class AnalysisResult(models.Model):
    FRESHNESS_LABEL_CHOICES = [
        ('good', 'Good'),
        ('bad', 'Bad'),
    ]

    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='analysis_results')
    freshness_score = models.IntegerField(null=True, blank=True)
    freshness_label = models.CharField(max_length=10, choices=FRESHNESS_LABEL_CHOICES, null=True, blank=True)
    defects_detected = models.JSONField(null=True, blank=True)  # Django handles JSON natively
    confidence_score = models.FloatField(null=True, blank=True)
    analyzed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis for Image {self.image.id}"
