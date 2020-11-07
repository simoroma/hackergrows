# from django.core.signals import request_finished
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

from urllib.parse import urlparse
from urllib.request import Request, urlopen
import re
from bs4 import BeautifulSoup

from .models import Item, Vote, Comment, Story


@receiver(pre_save)
def mark_show_and_ask(sender, instance, **kwargs):
    if isinstance(instance, Story):
        if instance.title.lower().startswith('ask'):
            instance.is_ask = True
        if instance.title.lower().startswith('show'):
            instance.is_show = True


@receiver(post_save)
def create_self_upvote_for_submission(sender, instance, created, **kwargs):
    if created and isinstance(instance, Item):
        vote = Vote(item=instance, user=instance.user)
        vote.save()


@receiver(post_save)
def check_for_duplicates(sender, instance, created, **kwargs):
    if created and isinstance(instance, Story):
        story = instance
        if story.original_url and story.product_url and story.duplicate_of is None:
            other_stories = Story.objects.filter(original_url=story.original_url,
                                                 product_url=story.product_url).exclude(pk=story.pk).order_by('-changed_at')
            c = other_stories.count()
            if c > 0:
                new_vote = Vote(item=other_stories[0], vote=1, user=story.user)
                new_vote.save()
                story.duplicate_of = other_stories[0]
                story.save()


@receiver(post_save)
def update_votes_count_on_submission(sender, instance, created, **kwargs):
    if created and isinstance(instance, Vote):
        vote = instance
        item = instance.item
        other_votes = Vote.objects.filter(
            item=vote.item, user=vote.user, vote=vote.vote).exclude(pk=vote.pk)
        if other_votes.count():
            return
        if instance.vote > 0:
            item.upvotes += instance.vote
        else:
            item.downvotes += (-1)*instance.vote
        item.points += instance.vote
        item.save()


@receiver(post_save)
def update_user_karma_on_vote(sender, instance, created, **kwargs):
    if created and isinstance(instance, Vote):
        vote = instance
        other_votes = Vote.objects.filter(
            item=vote.item, user=vote.user, vote=vote.vote).exclude(pk=vote.pk)
        if other_votes.count():
            return
        item = instance.item
        if item.user != instance.user:
            item.user.karma += instance.vote
            item.user.save()


def _recount_comments(instance, val=1):
    assert isinstance(instance, Comment)
    instance.to_story.num_comments += val
    instance.to_story.save()
    parent = instance.parent
    while parent is not None:
        parent.num_comments += val
        parent.save()
        parent = parent.parent


@receiver(post_save)
def update_comments_count_on_submission(sender, instance, created, **kwargs):
    if created and isinstance(instance, Comment):
        _recount_comments(instance, 1)


@receiver(post_delete)
def update_comments_count_on_deletion(sender, instance, **kwargs):
    if isinstance(instance, Comment):
        _recount_comments(instance, -1)


@receiver(post_delete)
def update_item_votes_on_unvote(sender, instance, **kwargs):
    if isinstance(instance, Vote):
        vote = instance
        item = vote.item
        if vote.user == item.user:
            return
        item.points -= vote.vote
        if vote.vote > 0:
            item.upvotes -= abs(vote.vote)
        else:
            item.downvotes -= abs(vote.vote)
        item.save()


@receiver(post_delete)
def update_user_karma_on_unvote(sender, instance, **kwargs):
    if isinstance(instance, Vote):
        vote = instance
        item = vote.item
        if vote.user == item.user:
            return
        item.user.karma -= vote.vote
        item.user.save()


@receiver(pre_save)
def add_domain_to_link_stories(sender, instance, **kwargs):
    if isinstance(instance, Story):
        if instance.original_url:
            o = urlparse(instance.original_url)
            instance.original_url_domain = o.hostname.lower()

        if instance.product_url:
            o = urlparse(instance.product_url)
            instance.product_url_domain = o.hostname.lower()


@receiver(pre_save)
def add_title(sender, instance, **kwargs):
    if isinstance(instance, Story):
        if not instance.title:
            instance.title = _get_title(url=instance.original_url,
                                        back_up_title=instance.original_url)
        if not instance.product_title:
            instance.product_title = _get_title(url=instance.product_url,
                                                back_up_title=instance.product_url)


def _get_title(url, back_up_title):
    try:
        req = Request(url)
        req.add_header('User-Agent', 'Hackergrows')
        req.add_header('Access-Control-Allow-Origin', '*')
        req.add_header('Access-Control-Allow-Methods', 'GET')
        req.add_header('Access-Control-Allow-Headers', 'Content-Type')
        req.add_header('Access-Control-Max-Age', '3600')
        webpage = urlopen(req, timeout=2).read()

        retitle = re.compile(
            "<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)

        match = retitle.search(webpage.decode('utf-8', errors='ignore'))
        if match:
            title = match.group(1).strip()
            # Parse HTML like &amp;
            soup = BeautifulSoup(title, 'html.parser')
            # Avoid to parse back again &, <, and >
            return soup.prettify(formatter=None)
        else:
            return back_up_title
    except Exception as e:
        print("Exception: {}".format(type(e).__name__))
        print("Exception message: {}".format(e))
        print(url)
        return back_up_title
