from django.contrib import admin
from .models import Post

# admin.site.register(Post)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
  list_display = ("id", "title", "content", "author", "created_at", "updated_at")
  list_editable = ("title", "author")
