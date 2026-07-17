from django.contrib.syndication.views import Feed  # Import Django's RSS feed base class.
from django.urls import reverse_lazy  # Import lazy URL resolver.
from Blog.models import Post  # Import the Post model.

# Create an RSS feed for the latest published blog posts.
class LatestPostsFeed(Feed):
    title = "Latest Posts"
    link = reverse_lazy('home')
    description = "Updates on new blog posts"

    # Return the 10 most recent active posts.
    def items(self):
        return Post.objects.filter(status="Active").order_by('-date')[:10]

    # Return the title of each feed item.
    def item_title(self, item):
        return item.title

    # Return the description of each feed item.
    def item_description(self, item):
        return item.description

    # Return the URL for each feed item.
    def item_link(self, item):
        return reverse_lazy('post_detail', args=[item.slug])
