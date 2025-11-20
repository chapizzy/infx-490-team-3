from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Produce(models.Model):
    name = models.CharField(max_length=255, null=False)
    category = models.CharField(max_length=255, null=False)
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

    produce = models.ForeignKey(Produce, on_delete=models.CASCADE)
    # Reference the project's configured user model to avoid hard-coding the auth model
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    # store uploaded image files using Django's ImageField so we can call `.save()` on it
    image_path = models.ImageField(upload_to='uploads/%Y/%m/%d/', null=True, blank=True)
    upload_timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
    )
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"Image {self.id} for {self.produce.name}"


class AnalysisResult(models.Model):
    FRESHNESS_LABELS = [
        ('good', 'Good'),
        ('bad', 'Bad'),
    ]

    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    # freshness_score: percentage-like (0-100)
    freshness_score = models.IntegerField(
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    freshness_label = models.CharField(
        max_length=10,
        choices=FRESHNESS_LABELS,
        null=True,
    )
    defects_detected = models.JSONField(null=True, blank=True)  # Django can store JSON natively
    confidence_score = models.FloatField(null=True)
    analyzed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis for Image {self.image.id}"


class Review(models.Model):
    # Use the configured user model for compatibility with the project's auth setup
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    produce = models.ForeignKey(Produce, on_delete=models.CASCADE)
    # rating: 1-5 expected
    rating = models.IntegerField(
        null=False,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user} for {self.produce.name}"


class Feedback(models.Model):
    """
    User feedback linked to an uploaded Image.
    Supports logged-in users (user FK) and anonymous visitors (session_key).
    """
    image = models.ForeignKey(
        Image,
        on_delete=models.CASCADE,
        related_name='feedbacks',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    is_helpful = models.BooleanField(null=True)
    explanation = models.TextField(blank=True, null=True)
    # store session key so we can track anonymous visitors across requests
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback {self.id} for Image {self.image.id} - helpful={self.is_helpful}"
