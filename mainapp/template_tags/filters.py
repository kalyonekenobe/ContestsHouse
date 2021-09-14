from django import template
from django.template.defaultfilters import date as datefilter
from django.utils.safestring import mark_safe
from mainapp.utils import *

register = template.Library()

COMMENT_PATTERN = {
    'header': """ <div class="comment """,
    'child_class': None,
    'body': """">
                      <div class="comment-header">
                          <div class="d-flex flex-wrap align-items-center">
                              <h6 class="mb-0 me-2">
            """,
    'author_value': None,
    'author': """</h6>
                    <a class="comment-reply td-none" reply-to='""",
    'reply_to_value': None,
    'reply_to': """'>Відповісти</a>
                          </div>
                          <span>
                """,
    'datetime_value': None,
    'datetime': """
                          </span>
                      </div>
                      <div class="comment-body">
                          <p>
                """,
    'text_value': None,
    'text': """
                          </p>
                      </div>
                      <div class="comment-children">
            """,
    'children': None,
    'footer': """
                      </div>
                  </div>
              """,
}


COMMENTS_CHECK_LIST = {}


def build_comment_dom(comment, comment_children_dom, parent):
    comment_values = {
        'child_class': '',
        'author_value': '<span class="username"><i class="bi bi-person-circle me-1"></i>' + str(comment.username) + '</span>',
        'reply_to_value': str(encode_value(comment.id)),
        'datetime_value': str(datefilter(comment.datetime, "d M Y, H:i")),
        'text_value': str(comment.text),
        'children': str(comment_children_dom),
    }
    
    comment_dom = ""
    
    if parent is not None:
        comment_values['child_class'] = 'child'
        comment_values['author_value'] = '<span class="username"><i class="bi bi-person-circle me-1"></i>' + comment.username + '</span>' + """
                                          <span class='status'> у відповідь на коментар користувача </span>
                                          """ + '<span class="username"><i class="bi bi-person-circle me-1"></i>' + parent.username + '</span>'
    
    for key, value in COMMENT_PATTERN.items():
        comment_dom += comment_values[key] if not value else value
    
    return comment_dom


def comment_dfs(comment, comment_children_dom, parent=None):
    COMMENTS_CHECK_LIST[comment.id] = True
    for child in comment.children.all():
        if not COMMENTS_CHECK_LIST.get(child.id):
            comment_children_dom += comment_dfs(child, "", comment)
    
    return build_comment_dom(comment, comment_children_dom, parent)


@register.filter
def startup_comments(startup):
    COMMENTS_CHECK_LIST.clear()
    if startup.comments.all():
        comments_dom = ""
        for comment in startup.comments.all():
            if not COMMENTS_CHECK_LIST.get(comment.id):
                comments_dom += comment_dfs(comment, "")
        return mark_safe(comments_dom)
    else:
        return mark_safe("<p class='information'>Коментарі відсутні <i class='bi bi-emoji-neutral ms-2'></i></p>")
