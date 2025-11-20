from django.contrib import admin
from .models import Produce, Image, AnalysisResult, Feedback


@admin.register(Produce)
class ProduceAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'category')


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
	list_display = ('id', 'produce', 'user', 'upload_timestamp', 'status')


@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
	list_display = ('id', 'image', 'freshness_label', 'confidence_score', 'analyzed_at')


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
	list_display = ('id', 'image', 'user', 'is_helpful', 'session_key', 'created_at')
