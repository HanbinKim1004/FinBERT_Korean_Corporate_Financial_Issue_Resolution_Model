from django.db import models

class Search(models.Model):
    keyword = models.TextField(default='', null=True, blank=True)

    def __str__(self):
        return self.keyword

class Company(models.Model):
    title = models.TextField(default='', null=True, blank=True)
    pos1 = models.TextField(default='', null=True, blank=True)
    pos2 = models.TextField(default='', null=True, blank=True)
    pos3 = models.TextField(default='', null=True, blank=True)
    pos4 = models.TextField(default='', null=True, blank=True)
    pos5 = models.TextField(default='', null=True, blank=True)
    neg1 = models.TextField(default='', null=True, blank=True)
    neg2 = models.TextField(default='', null=True, blank=True)
    neg3 = models.TextField(default='', null=True, blank=True)
    neg4 = models.TextField(default='', null=True, blank=True)
    neg5 = models.TextField(default='', null=True, blank=True)

    def __str__(self):
        return self.title