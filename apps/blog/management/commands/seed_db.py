import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from datetime import timedelta

from apps.accounts.models import User
from apps.profiles.models import Profile
from apps.blog.models import Category, Post
from apps.comments.models import Comment
from apps.likes.models import Like
from apps.follows.models import Follow
from apps.bookmarks.models import Bookmark
from apps.notifications.models import Notification
from apps.dashboard.models import DashboardStats


CATEGORIES = [
    'Technology', 'Travel', 'Food', 'Lifestyle', 'Health',
    'Education', 'Business', 'Entertainment', 'Sports', 'Science',
]

USERS = [
    ('alice@example.com', 'Alice Johnson', 'Alice is a software engineer who loves teaching others.'),
    ('bob@example.com', 'Bob Smith', 'Bob travels the world and writes about it.'),
    ('carol@example.com', 'Carol Williams', 'Carol is a nutrition coach and food blogger.'),
    ('dave@example.com', 'Dave Brown', 'Dave covers tech news and AI trends.'),
    ('erin@example.com', 'Erin Davis', 'Erin is a fitness enthusiast and yoga instructor.'),
    ('frank@example.com', 'Frank Miller', 'Frank writes about business and startups.'),
]

POSTS = [
    {
        'title': 'Getting Started with Django 5',
        'category': 'Technology',
        'tags': ['django', 'python', 'web'],
        'content': '<p>Django 5 brings many exciting features including improved async support, '
                   'better performance, and new middleware capabilities. In this post, we explore the '
                   'key features and how to get started with Django for your next web project.</p>'
                   '<p>First, make sure you have Python 3.13 or later installed. Then install Django '
                   'using pip: <code>pip install django</code>. Create a new project with '
                   '<code>django-admin startproject mysite</code>.</p>',
        'excerpt': 'A beginner-friendly introduction to building web apps with Django 5.',
    },
    {
        'title': 'Top 10 Travel Destinations in 2026',
        'category': 'Travel',
        'tags': ['travel', 'destinations', '2026'],
        'content': '<p>Traveling opens up new horizons and experiences. Here are the top 10 destinations '
                   'you should visit in 2026. From the serene beaches of Bali to the historic streets '
                   'of Rome, each destination offers something unique.</p>'
                   '<p>Whether you are an adventure seeker or a culture enthusiast, there is a place for '
                   'everyone on this list.</p>',
        'excerpt': 'Plan your next adventure with our curated list of must-visit places.',
    },
    {
        'title': 'Healthy Eating Habits for Busy Professionals',
        'category': 'Health',
        'tags': ['health', 'nutrition', 'productivity'],
        'content': '<p>Maintaining a healthy diet while managing a busy schedule can be challenging. '
                   'This post shares practical tips for meal prepping, choosing the right snacks, and '
                   'staying hydrated throughout the day.</p>'
                   '<p>Small changes in your eating habits can lead to significant improvements in your '
                   'overall health and productivity.</p>',
        'excerpt': 'Simple, actionable nutrition tips for people with packed schedules.',
    },
    {
        'title': 'The Future of Artificial Intelligence',
        'category': 'Technology',
        'tags': ['ai', 'machine-learning', 'future'],
        'content': '<p>Artificial Intelligence is transforming industries across the globe. From healthcare '
                   'to finance, AI is enabling new possibilities that were once thought impossible. In this '
                   'article, we discuss the latest trends and what the future holds for AI.</p>'
                   '<p>Key areas of growth include natural language processing, computer vision, and '
                   'autonomous systems.</p>',
        'excerpt': 'How AI is reshaping every major industry and what comes next.',
    },
    {
        'title': 'How to Build a Personal Brand',
        'category': 'Business',
        'tags': ['branding', 'career', 'marketing'],
        'content': '<p>Building a personal brand is essential in today\'s digital world. Whether you are '
                   'an entrepreneur, freelancer, or professional, a strong personal brand can open doors '
                   'to new opportunities.</p>'
                   '<p>Start by defining your unique value proposition, creating consistent content, and '
                   'engaging with your audience authentically.</p>',
        'excerpt': 'A step-by-step guide to crafting a memorable personal brand.',
    },
    {
        'title': 'Mastering Time Management',
        'category': 'Lifestyle',
        'tags': ['productivity', 'habits', 'focus'],
        'content': '<p>Time management is a critical skill for achieving your goals. Learn about the '
                   'Pomodoro Technique, Eisenhower Matrix, and other proven strategies to make the most '
                   'of your time.</p>'
                   '<p>By prioritizing tasks and minimizing distractions, you can accomplish more in less '
                   'time while maintaining a healthy work-life balance.</p>',
        'excerpt': 'Practical frameworks to take control of your day and boost focus.',
    },
    {
        'title': 'Exploring the Wonders of Space',
        'category': 'Science',
        'tags': ['space', 'astronomy', 'science'],
        'content': '<p>Space exploration has always captivated human imagination. From the Apollo missions '
                   'to the latest Mars rovers, we continue to push the boundaries of what is possible.</p>'
                   '<p>Join us as we explore the latest discoveries in astronomy and the future of space '
                   'travel.</p>',
        'excerpt': 'A tour of the cosmos and humanity\'s quest to explore it.',
    },
    {
        'title': 'The Art of Home Cooking',
        'category': 'Food',
        'tags': ['cooking', 'recipes', 'food'],
        'content': '<p>Cooking at home is not only economical but also a great way to express creativity. '
                   'Learn essential techniques, explore new recipes, and discover the joy of preparing '
                   'meals from scratch.</p>'
                   '<p>From beginner-friendly dishes to gourmet creations, home cooking has something '
                   'for everyone.</p>',
        'excerpt': 'Rediscover the pleasure of cooking delicious meals at home.',
    },
    {
        'title': 'Online Learning Platforms Comparison',
        'category': 'Education',
        'tags': ['education', 'elearning', 'courses'],
        'content': '<p>With the rise of online education, choosing the right learning platform is crucial. '
                   'We compare popular platforms like Coursera, Udemy, and edX to help you make an '
                   'informed decision.</p>'
                   '<p>Consider factors such as course quality, pricing, certification, and community '
                   'support when selecting a platform.</p>',
        'excerpt': 'Which online learning platform is right for you? We compare the top options.',
    },
    {
        'title': 'Understanding Cryptocurrency',
        'category': 'Business',
        'tags': ['crypto', 'blockchain', 'finance'],
        'content': '<p>Cryptocurrency has revolutionized the financial landscape. In this comprehensive '
                   'guide, we explain blockchain technology, Bitcoin, Ethereum, and other major '
                   'cryptocurrencies.</p>'
                   '<p>Learn about the benefits, risks, and regulatory considerations associated with '
                   'digital currencies.</p>',
        'excerpt': 'Demystifying blockchain, Bitcoin, and the world of digital money.',
    },
    {
        'title': 'Best Hiking Trails in 2026',
        'category': 'Travel',
        'tags': ['hiking', 'outdoors', 'travel'],
        'content': '<p>There is nothing quite like the fresh air and breathtaking views of a great hiking '
                   'trail. We have rounded up the best trails to explore this year, from coastal cliffs '
                   'to mountain ridges.</p>'
                   '<p>Pack your gear, lace up your boots, and get ready for an unforgettable '
                   'outdoor adventure.</p>',
        'excerpt': 'Lace up and hit the trail with our favorite hikes for the year.',
    },
    {
        'title': 'Mindfulness for Everyday Life',
        'category': 'Health',
        'tags': ['mindfulness', 'wellbeing', 'mental-health'],
        'content': '<p>Mindfulness is the practice of being present in the moment. Incorporating small '
                   'mindful habits into your daily routine can reduce stress and improve focus.</p>'
                   '<p>Try a short breathing exercise each morning and notice the difference it makes.</p>',
        'excerpt': 'Simple mindfulness practices to bring calm into a busy life.',
    },
]

COMMENT_SNIPPETS = [
    'Great post, thanks for sharing!',
    'This was really helpful, learned a lot.',
    'I completely agree with your points here.',
    'Could you write a follow-up on this topic?',
    'Awesome read, bookmarking this for later.',
    'Very insightful, keep up the good work!',
]


class Command(BaseCommand):
    help = 'Seed the database with demo users, posts, and social interactions.'

    def handle(self, *args, **kwargs):
        users = self._create_users()
        categories = self._create_categories()
        posts = self._create_posts(users, categories)
        self._create_interactions(users, posts)
        self._create_dashboard_stats(users)
        self.stdout.write(self.style.SUCCESS(
            f'Seeded {len(users)} users, {len(categories)} categories, '
            f'{len(posts)} posts, plus comments, likes, follows, bookmarks, '
            f'notifications and dashboard stats.'
        ))

    def _create_users(self):
        users = []
        for email, full_name, bio in USERS:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={'full_name': full_name, 'is_email_verified': True},
            )
            if created:
                user.set_password('password123')
                user.save()
            Profile.objects.get_or_create(
                user=user,
                defaults={
                    'bio': bio,
                    'location': random.choice(['New York', 'London', 'Berlin', 'Tokyo', 'Sydney']),
                    'website': f'https://{email.split("@")[0]}.example.com',
                    'gender': random.choice(['male', 'female', 'other']),
                },
            )
            users.append(user)
            self.stdout.write(f'User: {user.email}')
        return users

    def _create_categories(self):
        categories = []
        for name in CATEGORIES:
            cat, _ = Category.objects.get_or_create(
                title=name,
                defaults={'slug': slugify(name)},
            )
            categories.append(cat)
        self.stdout.write(f'Categories: {len(categories)}')
        return categories

    def _create_posts(self, users, categories):
        posts = []
        cat_map = {c.title: c for c in categories}
        for i, data in enumerate(POSTS, 1):
            author = random.choice(users)
            category = cat_map.get(data['category'])
            base_slug = slugify(data['title'])
            slug = f'{base_slug}-{i}'
            while Post.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{random.randint(1, 9999)}'
            post = Post.objects.create(
                user=author,
                title=data['title'],
                slug=slug,
                content=data['content'],
                excerpt=data['excerpt'],
                category=category,
                status='published',
                views=random.randint(50, 5000),
                likes_count=random.randint(0, 500),
                comments_count=random.randint(0, 100),
                shares_count=random.randint(0, 50),
                published_at=timezone.now() - timedelta(days=random.randint(1, 60)),
            )
            for tag in data['tags']:
                post.tags.add(tag)
            posts.append(post)
            self.stdout.write(f'Post: {post.title}')
        return posts

    def _create_interactions(self, users, posts):
        # Comments
        for post in posts:
            n = random.randint(1, 4)
            for _ in range(n):
                commenter = random.choice(users)
                Comment.objects.get_or_create(
                    post=post,
                    user=commenter,
                    comment=random.choice(COMMENT_SNIPPETS),
                    defaults={'name': commenter.full_name or commenter.username,
                             'email': commenter.email,
                             'is_approved': True},
                )
                if commenter != post.user:
                    Notification.objects.get_or_create(
                        user=post.user,
                        post=post,
                        type='comment',
                        message=f'{commenter.full_name or commenter.username} commented on your post.',
                    )

        # Likes
        for post in posts:
            likers = random.sample(users, k=random.randint(1, len(users)))
            for liker in likers:
                like, created = Like.objects.get_or_create(user=liker, post=post)
                if created and liker != post.user:
                    Notification.objects.get_or_create(
                        user=post.user,
                        post=post,
                        type='like',
                        message=f'{liker.full_name or liker.username} liked your post.',
                    )

        # Follows
        for follower in users:
            followees = random.sample(users, k=random.randint(1, 3))
            for followee in followees:
                if followee == follower:
                    continue
                Follow.objects.get_or_create(follower=follower, following=followee)
                Notification.objects.get_or_create(
                    user=followee,
                    type='follow',
                    message=f'{follower.full_name or follower.username} started following you.',
                )

        # Bookmarks
        for post in posts:
            bookers = random.sample(users, k=random.randint(0, 2))
            for booker in bookers:
                Bookmark.objects.get_or_create(user=booker, post=post)
                if booker != post.user:
                    Notification.objects.get_or_create(
                        user=post.user,
                        post=post,
                        type='bookmark',
                        message=f'{booker.full_name or booker.username} bookmarked your post.',
                    )

    def _create_dashboard_stats(self, users):
        for user in users:
            DashboardStats.objects.update_or_create(
                user=user,
                defaults={
                    'total_posts': user.posts.filter(status='published').count(),
                    'total_views': sum(p.views for p in user.posts.all()),
                    'total_likes': user.likes.count(),
                    'total_comments': user.comments.count(),
                    'total_followers': user.followers.count(),
                    'total_bookmarks': user.bookmarks.count(),
                },
            )