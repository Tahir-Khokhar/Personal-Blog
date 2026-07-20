from django.urls import path, include


# Bridge legacy API under the new /api/ prefix.
# This will be replaced by fully modular apps/api viewsets in later phases.
urlpatterns = [
    path('', include('Blog.urls')),
    # Swagger/OpenAPI schema and UI will be added in Phase 2.
]



