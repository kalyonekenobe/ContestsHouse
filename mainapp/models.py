from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse
from django.utils import timezone


class File(models.Model):
    
    name = models.CharField(max_length=255, verbose_name="Назва")
    file = models.FileField()
    
    def __str__(self):
        return self.name
    
    def extension(self):
        return self.name.split('.')[-1]
    
    def filename(self):
        return self.file.name
    

class Category(models.Model):
    
    name = models.CharField(max_length=255, verbose_name="Назва")
    slug = models.SlugField(max_length=255, verbose_name="Унікальне ім'я", unique=True)
    
    def __str__(self):
        return f"Категорія: { self.name }"


class StartupMember(models.Model):
    
    user = models.ForeignKey(User, verbose_name='Користувач', on_delete=models.CASCADE)
    middle_name = models.CharField(max_length=64, verbose_name='По-батькові', blank=True)
    phone = models.CharField(max_length=32, verbose_name="Номер телефону", blank=True)
    birth_date = models.DateField(null=True, blank=True)
    date_of_accession = models.DateTimeField(default=timezone.now)
    image = models.ImageField(verbose_name="Зображення", blank=True)
    role = models.CharField(max_length=255, verbose_name="Роль у стартапі")
    
    def __str__(self):
        return f"{self.user.last_name} {self.user.first_name} {self.middle_name}: {self.role}"
    
    def get_full_name(self):
        return f"{self.user.last_name} {self.user.first_name} {self.middle_name}"


class Feedback(models.Model):
    
    username = models.CharField(max_length=255, verbose_name="Ім'я користувача")
    user_ip = models.CharField(max_length=255, verbose_name="ІР користувача")
    text = models.TextField(verbose_name="Відгук")
    datetime = models.DateTimeField(default=timezone.now, verbose_name="Дата та час створення")
    visible = models.BooleanField(default=False, verbose_name="Відобразити на сайті")
    
    def __str__(self):
        return f"Відгук №{ self.id }"


class Comment(models.Model):
    username = models.CharField(max_length=255, verbose_name="Ім'я користувача")
    user_ip = models.CharField(max_length=255, verbose_name="ІР користувача")
    text = models.TextField(verbose_name="Коментар")
    attached_files = models.ManyToManyField(File, verbose_name="Вкладені файли", related_name='related_comment_attached_files', blank=True)
    datetime = models.DateTimeField(default=timezone.now, verbose_name="Дата та час створення")
    children = models.ManyToManyField('self', verbose_name="Відповіді до цього коментаря", blank=True)
    
    def __str__(self):
        return f"Коментар #: { self.id }"
    

class Post(models.Model):
    
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    text = models.TextField(verbose_name="Текст")
    image = models.ImageField(verbose_name="Зображення")
    author = models.ForeignKey(User, verbose_name="Автор", on_delete=models.CASCADE)
    datetime = models.DateTimeField(default=timezone.now, verbose_name="Дата та час створення")
    attached_files = models.ManyToManyField(File, verbose_name="Вкладені файли", related_name="related_post_attached_files", blank=True)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'id': self.id})


class Startup(models.Model):
    
    STATUS_TEAM_SET = 'team-set'
    STATUS_IN_DEVELOPMENT = 'in-development'
    STATUS_PAUSED = 'paused'
    STATUS_CANCELED = 'canceled'
    STATUS_FINISHED = 'finished'
    STATUS_TESTING = 'testing'
    STATUS_PROMOTED = 'promoted'
    
    STATUS_CHOICES = (
        (STATUS_TEAM_SET, 'Набір учасників'),
        (STATUS_IN_DEVELOPMENT, 'У розробці'),
        (STATUS_PAUSED, 'Призупинено'),
        (STATUS_CANCELED, 'Відмінено'),
        (STATUS_FINISHED, 'Завершено'),
        (STATUS_TESTING, 'Тестується'),
        (STATUS_PROMOTED, 'У процесі просування'),
    )
    
    STATUS_NAMES = {
        STATUS_TEAM_SET: 'Набір учасників',
        STATUS_IN_DEVELOPMENT: 'У розробці',
        STATUS_PAUSED: 'Призупинено',
        STATUS_CANCELED: 'Відмінено',
        STATUS_FINISHED: 'Завершено',
        STATUS_TESTING: 'Тестується',
        STATUS_PROMOTED: 'У процесі просування',
    }
    
    name = models.CharField(max_length=255, verbose_name="Назва")
    slug = models.SlugField(max_length=255, verbose_name="Унікальне ім'я", unique=True)
    image = models.ImageField(verbose_name="Зображення", null=True, blank=True)
    short_description = models.TextField(verbose_name="Короткий опис", null=True)
    description = models.TextField(verbose_name="Опис")
    categories = models.ManyToManyField(Category, verbose_name="Категорії, до яких відноситься проект", related_name='related_categories')
    creator = models.ForeignKey(User, verbose_name='Автор', on_delete=models.CASCADE)
    members = models.ManyToManyField(StartupMember, verbose_name="Учасники", related_name='related_members', blank=True)
    status = models.CharField(max_length=32, verbose_name="Статус", choices=STATUS_CHOICES, default=STATUS_TEAM_SET)
    datetime = models.DateTimeField(verbose_name="Дата та час створення", default=timezone.now)
    followers = models.ManyToManyField(User, verbose_name="Підписники", related_name='related_followers', blank=True)
    budget = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="Бюджет проекту", default=0)
    files = models.ManyToManyField(File, verbose_name="Вкладені файли", blank=True)
    comments = models.ManyToManyField(Comment, verbose_name="Коментарі", related_name='related_comments', blank=True)
    
    def __str__(self):
        return f"Проект №{ self.id }: { self.name }"
    
    def get_absolute_url(self):
        return reverse('startup_detail', kwargs={'slug': self.slug})
    
    def status_name(self):
        return self.STATUS_NAMES[self.status]
    