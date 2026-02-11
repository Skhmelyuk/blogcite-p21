from django.contrib import admin
from .models import Post, Category, Comment
from django.utils.html import format_html


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
  list_display = ("id", "title", "author", "category", "image_tag", "created_at", "likes", "views")
  list_editable = ("title", "author") 
  prepopulated_fields = {"slug": ("title",)}
  list_filter = ("created_at", "updated_at", "category") 
  search_fields = ("title", "content")

  def image_tag(self, obj):
      if obj.image:
          return format_html(
              '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px" />',
                obj.image.url,
            )
      return format_html('<span>не має зображення</span>')
    
  image_tag.short_description = "Image"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
  list_display = ("id", "name", "slug")
  list_editable = ("name", "slug")
  prepopulated_fields = {"slug": ("name",)}


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "post", "short_body", "created_at")
    list_filter = ("created_at", "author")
    search_fields = ("body", "author__username", "post__title")

    def short_body(self, obj):
        return obj.body[:50] + "..." if len(obj.body) > 50 else obj.body
    short_body.short_description = "Текст"