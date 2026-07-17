from django.contrib.auth.password_validation import validate_password  # Import Django's password validator.
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer  # Import JWT token serializer.
from rest_framework import serializers  # Import Django REST Framework serializers.
from rest_framework.validators import UniqueValidator  # Import unique field validator.

from Blog import models as Blog_models  # Import blog models.


# Customize the JWT token with additional user information.
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    # Add custom user information to the JWT token.
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['full_name'] = user.full_name
        token['email'] = user.email
        token['username'] = user.username
        return token


# Serializer for user registration.
class RegisterSerializer(serializers.ModelSerializer):
    # Validate the password using Django's built-in validators.
    password = serializers.CharField(
        write_only=True,  # Hide this field from API responses.
        required=True,    # Make this field required.
        validators=[validate_password]
    )

    # Confirm the user's password.
    password2 = serializers.CharField(
        write_only=True,  # Hide this field from API responses.
        required=True     # Make this field required.
    )

    # Configure serializer options.
    class Meta:
        model = Blog_models.User
        fields = ('full_name', 'email', 'password', 'password2')
        extra_kwargs = {
            'email': {
                # Ensure the email address is unique.
                'validators': [
                    UniqueValidator(queryset=Blog_models.User.objects.all())
                ]
            },
        }

    # Validate that both password fields match.
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    # Create and return a new user account.
    def create(self, validated_data):
        validated_data.pop('password2')
        return Blog_models.User.objects.create_user(
            email=validated_data['email'],
            full_name=validated_data.get('full_name', ''),
            password=validated_data['password'],
        )


# Serializer for user information.
class UserSerializer(serializers.ModelSerializer):

    # Configure serializer options.
    class Meta:
        model = Blog_models.User
        fields = ('id', 'username', 'email', 'full_name')


# Serializer for user profile information.
class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # Include user details as read-only.

    # Configure serializer options.
    class Meta:
        model = Blog_models.Profile
        fields = (
            'id', 'user', 'image', 'full_name', 'bio', 'about',
            'author', 'country', 'facebook', 'twitter', 'date'
        )


# Serializer for requesting a password reset.
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


# Serializer for confirming a password reset.
class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField()

    # Validate the new password.
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )

    # Confirm the new password.
    password2 = serializers.CharField(write_only=True)

    # Validate that both password fields match.
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

# Serializer for changing the current password.
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()

    # Validate the new password.
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )

    # Confirm the new password.
    password2 = serializers.CharField(write_only=True)

    # Validate that both password fields match.
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

# Serializer for blog categories.
class CategorySerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()  # Return computed post count.

    # Configure serializer options.
    class Meta:
        model = Blog_models.Category
        fields = ("id", "title", "image", "slug", "post_count")

    # Return the total number of posts in the category.
    def get_post_count(self, category):
        return category.posts.count()

# Serializer for blog comments and replies.
class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()  # Return nested replies.

    # Configure serializer options.
    class Meta:
        model = Blog_models.Comment
        fields = (
            "id", "post", "parent", "user", "name", "email",
            "comment", "reply", "is_approved", "date", "replies"
        )
        read_only_fields = ("is_approved", "date", "reply")

    # Return all replies for a comment.
    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(
                obj.replies.all(),
                many=True,
                context=self.context
            ).data
        return []

# Serializer for blog posts.
class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(
        many=True,
        read_only=True
    )  # Include related comments.

    tags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )  # Return tag names.

    like_count = serializers.IntegerField(
        source='likes.count',
        read_only=True
    )  # Return total likes.

    # Configure serializer options.
    class Meta:
        model = Blog_models.Post
        fields = (
            "id", "user", "title", "image", "description", "content",
            "tags", "category", "status", "featured", "view",
            "likes", "like_count", "slug", "date", "publish_at",
            "comments"
        )
        read_only_fields = ("user", "slug", "view", "likes", "date")

# Serializer for follow relationships.
class FollowSerializer(serializers.ModelSerializer):

    # Configure serializer options.
    class Meta:
        model = Blog_models.Follow
        fields = ("id", "follower", "following", "date")

# Serializer for bookmarked posts.
class BookmarkSerializer(serializers.ModelSerializer):

    # Configure serializer options.
    class Meta:
        model = Blog_models.Bookmark
        fields = ("id", "user", "post", "date")
        read_only_fields = ("user",)

# Serializer for user notifications.
class NotificationSerializer(serializers.ModelSerializer):

    # Configure serializer options.
    class Meta:
        model = Blog_models.Notification
        fields = ("id", "user", "post", "type", "seen", "date")
        read_only_fields = ("user", "post", "type")

# Serializer for author dashboard statistics.
class AuthorStatsSerializer(serializers.Serializer):
    views = serializers.IntegerField()       # Store total views.
    posts = serializers.IntegerField()       # Store total posts.
    likes = serializers.IntegerField()       # Store total likes.
    bookmarks = serializers.IntegerField()   # Store total bookmarks.
    followers = serializers.IntegerField()   # Store total followers.
