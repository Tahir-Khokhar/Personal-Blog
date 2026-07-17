from django import forms  # Import Django's built-in form module.
from Blog.models import Comment, Post, EmailSubscription  # Import models for form creation.

# Form for submitting blog comments.
class CommentForm(forms.ModelForm):  # Inherit from ModelForm to create a form from a model.
    class Meta:  # Configure form options.
        model = Comment  # Model associated with this form.
        fields = ['name', 'email', 'comment']  # Fields to include in the form.
        widgets = {  # Customize the HTML input widgets.
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),  # Single-line text input.
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),  # Email input with validation.
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Your Comment'}),  # Multi-line text area.
        }

# Form for creating and editing blog posts.
class PostForm(forms.ModelForm):  # Generate a form from the Post model.
    class Meta:  # Configure form options.
        model = Post  # Model associated with this form.
        fields = ['title', 'image', 'description', 'content', 'tags', 'category', 'status', 'publish_at']  # Form fields.
        widgets = {  # Customize the HTML input widgets.
            'title': forms.TextInput(attrs={'class': 'form-control'}),  # Single-line text input.
            'description': forms.Textarea(attrs={'class': 'form-control'}),  # Multi-line text area.
            'content': forms.Textarea(attrs={'class': 'form-control'}),  # Multi-line text area.
            'status': forms.Select(attrs={'class': 'form-control'}),  # Dropdown selection field.
            'publish_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),  # Date and time input.
        }

# Form for email subscriptions.
class SubscriptionForm(forms.ModelForm):  # Generate a form from the EmailSubscription model.
    class Meta:  # Configure form options.
        model = EmailSubscription  # Model associated with this form.
        fields = ['email']  # Include only the email field.
        widgets = {  # Customize the HTML input widget.
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),  # Email input with validation.
        }
