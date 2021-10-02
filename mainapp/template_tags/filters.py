from django import template
from django.template.defaultfilters import date
from django.utils.safestring import mark_safe
from django.contrib.staticfiles.storage import staticfiles_storage
from mainapp.utils import *

register = template.Library()

COMMENTS_CHECK_LIST = dict()

COMMENT_PATTERN = {
    0: """ <div class="comment """,
    'class': None,
    1: """">
                      <div class="comment-header">
                          <div class="d-flex flex-wrap align-items-center">
                              <h6 class="mb-0 me-2">
            """,
    'author': None,
    2: """</h6>
                    <a class="comment-reply td-none" reply-to='""",
    'reply_to': None,
    3: """'>Відповісти</a>
                          </div>
                          <span>
                """,
    'datetime': None,
    4: """
                          </span>
                      </div>
                      <div class="comment-body">
                          <p>
                """,
    'text': None,
    5: """
                          </p>
                      </div>
                      <div class='flex-wrap attached-files'>
        """,
    'attached_files': None,
    6: """
                      </div>
                      <div class="comment-children">
            """,
    'children': None,
    7: """
                      </div>
                  </div>
              """,
}


def build_comment_tree(comment, comment_tree, parent):
    
    attached_files = comment.attached_files.all()
    attached_files_html = ""
    if attached_files:
        attached_files_html = """<p class='w-100 mb-2'>Вкладені файли:</p>"""
        for file in attached_files:
            attached_files_html += """
                                       <div class="form-file" tooltip='Назва файлу: """ + file.name + """'>
                                           <img src='""" + staticfiles_storage.url(get_file_extension_image(file.extension())) + """'/>
                                           <span>
                                               <a href='""" + file.file.url + """' target='_blank'>
                                                   """ + file.name + """
                                               </a>
                                           </span>
                                       </div>
                                   """
        
    comment_values = {
        'class': '',
        'author': '<span class="username"><i class="bi bi-person-circle me-1"></i>' + comment.username + '</span>',
        'reply_to': encode_value(comment.id),
        'datetime': date(comment.datetime, "d M Y, H:i"),
        'text': comment.text,
        'attached_files': attached_files_html,
        'children': comment_tree,
    }
    
    comment_prototype = ''
    
    if parent is not None:
        comment_values['class'] = "child"
        comment_values['author'] = """
                                       <span class="username"><i class="bi bi-person-circle me-1"></i>
                                   """ + comment.username + """
                                       </span>
                                       <span class='status'> у відповідь на коментар користувача </span>
                                       <span class="username"><i class="bi bi-person-circle me-1"></i>
                                   """ + parent.username + """
                                       </span>
                                   """
    
    for key, value in COMMENT_PATTERN.items():
        comment_prototype += comment_values[key] if not value else value
    
    return comment_prototype


def comment_dfs(comment, parent=None):
    COMMENTS_CHECK_LIST[comment.id] = True
    comment_tree = ''
    for child in comment.children.all():
        if not COMMENTS_CHECK_LIST.get(child.id):
            comment_tree += comment_dfs(child, comment)
    
    return build_comment_tree(comment, comment_tree, parent)


@register.filter
def startup_comments(startup):
    COMMENTS_CHECK_LIST.clear()
    comment_tree = ''
    if startup.comments.all():
        for comment in startup.comments.all():
            if not COMMENTS_CHECK_LIST.get(comment.id):
                comment_tree = comment_dfs(comment) + comment_tree
    if not comment_tree:
        comment_tree = '<p class="information">Коментарі відсутні <i class="bi bi-emoji-neutral ms-2"></i></p>'
    return mark_safe(comment_tree)


@register.filter
def get_file_extension_image(file_extension):
    
    extension_names = {
        'archive': ('7z', 's7z', 'ace', 'afa', 'alz', 'apk', 'arc', 'ark', 'cdx', 'arj', 'b1', 'b6z', 'ba', 'bh', 'cab', 'car', 'cfs', 'cpt', 'dar', 'dd', 'dgc', 'dmg', 'ear', 'gca', 'genozip', 'ha', 'hki', 'ice', 'jar', 'kgb', 'lzh', 'lha', 'lzx', 'pak', 'partimg', 'paq6', 'paq7', 'paq8', 'pea', 'phar', 'pim', 'pit', 'qda', 'rar', 'rk', 'sda', 'sea', 'sen', 'sfx', 'shk', 'sit', 'sitx', 'sqx', 'tar.gz', 'tgz', 'tar.Z', 'tar.bz2', 'tbz2', 'tar.lz', 'tlz', 'tar.xz', 'txz', 'tar.zst', 'uc', 'uc0', 'uc2', 'ucn', 'ur2', 'ue2', 'uca', 'uha', 'war', 'wim', 'xar', 'xp3', 'yz1', 'zip', 'zipx', 'zoo', 'zpaq', 'zz'),
        'audio': ('3gp', 'aa', 'aac', 'aax', 'act', 'aiff', 'alac', 'amr', 'ape', 'au', 'awb', 'dss', 'dvf', 'flac', 'gsm', 'iklax', 'ivs', 'm4a', 'm4b', 'm4p', 'mmf', 'mp3', 'mpc', 'msv', 'nmf', 'ogg', 'oga', 'mogg', 'opus', 'ra', 'rm', 'raw', 'rf64', 'sln', 'tta', 'voc', 'vox', 'wav', 'wma', 'wv', 'webm', '8svx', 'cda'),
        'bookmark': ('json', 'one'),
        'excel': ('xlsx', 'xlsm', 'xlsb', 'xltx', 'xltm', 'xla', 'xlam', 'xll', 'xlw', 'xls', 'xlt', 'xlm'),
        'illustrator': ('ai', 'ait'),
        'image': ('jpeg', 'jfif', 'exif', 'tiff', 'gif', 'bpm', 'png', 'ppm', 'pgm', 'pbm', 'pnm', 'webp', 'hdr', 'heif', 'bat', 'cgm', 'rs-274x', 'svg', 'xaml', 'pict', 'mpo', 'pns', 'jps', 'eps'),
        'outlook': ('pst', 'ost'),
        'pdf': ('pdf'),
        'photoshop': ('psd'),
        'powerpoint': ('ppt', 'pot', 'pps', 'pptx', 'pptm', 'potx', 'potm', 'ppam', 'ppsx', 'ppsm', 'sldx', 'sldm'),
        'qrcode': ('eps'),
        'table': ('accdb', 'accde', 'accdt', 'accdr', 'sql'),
        'text': ('odt', 'rtf', 'tex', 'txt', 'wpd'),
        'video': ('webm', 'mkv', 'flv', 'vob', 'ogv', 'ogg', 'drc', 'gifv', 'mng', 'avi', 'mts', 'm2ts', 'ts', 'mov', 'qt', 'wmv', 'yuv', 'rm', 'rmvb', 'viv', 'asf', 'amv', 'mp4', 'm4v', 'mpg', 'mp2', 'mpeg', 'mpe', 'mpv', 'mpg', 'm2v', 'svi', '3gp', '3g2', 'mxf', 'roq', 'nsv', 'f4v', 'f4p', 'f4a', 'f4b'),
        'word': ('doc', 'docm', 'docx', 'dot', 'wbk', 'dotx', 'dotm', 'docb'),
    }
    
    image_path = 'file.png'
    
    for image_name in extension_names:
        if file_extension in extension_names[image_name]:
            image_path = image_name + '.png'
    
    return image_path

