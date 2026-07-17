from django.db import models  # Import Django's database models and expressions.
from django.conf import settings  # Import project settings.
from django.utils import timezone  # Import timezone utilities.
from datetime import timedelta  # Import timedelta for date calculations.
from Blog.models import Visitor  # Import the Visitor model.

# Middleware to track visitor sessions and page visits.
class VisitorCountMiddleware:
    # Initialize the middleware with the next request handler.
    def __init__(self, get_response):
        self.get_response = get_response

    # Process each request and update the visitor count.
    def __call__(self, request):
        response = self.get_response(request)  # Process the request first.

        try:
            visitor_id = request.session.session_key  # Get the current session key.

            if visitor_id:
                today = timezone.now().date()  # Get today's date.

                defaults = {
                    'date': today,
                    'count': 1,
                }

                # Create a new visitor record or retrieve the existing one.
                obj, created = Visitor.objects.get_or_create(
                    session_key=visitor_id,
                    date=today,
                    defaults=defaults
                )

                # Increase the visit count if the visitor already exists.
                if not created:
                    obj.count = models.F('count') + 1  # Increment count in the database.
                    obj.save()  # Save the updated count.

        except Exception:
            pass  # Ignore any errors during visitor tracking.

        return response  # Return the response to the client.
