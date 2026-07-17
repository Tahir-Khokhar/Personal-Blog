from django.contrib.sitemaps import Sitemap  # Import Django's sitemap base class.
from Blog.models import Post, Category  # Import blog models.

# Sitemap for published blog posts.
class PostSitemap(Sitemap):
    changefreq = "weekly"  # Indicate that posts are updated weekly.
    priority = 0.8  # Set the search engine priority.

    # Return all active blog posts.
    def items(self):
        return Post.objects.filter(status="Active")

    # Return the last modified date of each post.
    def lastmod(self, obj):
        return obj.date

    # Return the URL of each post.
    def location(self, obj):
        return f"/post/{obj.slug}/"


# Sitemap for blog categories.
class CategorySitemap(Sitemap):
    changefreq = "monthly"  # Indicate that categories are updated monthly.
    priority = 0.6  # Set the search engine priority.

    # Return all blog categories.
    def items(self):
        return Category.objects.all()

    # Return the URL of each category.
    def location(self, obj):
        return f"/category/{obj.slug}/"
