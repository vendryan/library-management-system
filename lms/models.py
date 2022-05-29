from datetime import datetime
from django.db import models


# Create your models here.
class Author(models.Model):
    author_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)

    # Buat index supaya lookup lebih efisien
    # See https://stackoverflow.com/questions/45328826/django-model-fields-indexing
    class Meta():
        indexes = [
            models.Index(fields=['name'])
        ]
    
    def __str__(self):
        return self.name


class Publisher(models.Model):
    publisher_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)

    # Buat index supaya lookup lebih efisien
    # See https://stackoverflow.com/questions/45328826/django-model-fields-indexing
    class Meta():
        indexes = [
            models.Index(fields=['name'])
        ]
    
    def __str__(self):
        return self.name


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Borrower(models.Model):
    borrower_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    contact = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.name} - {self.contact}'


class Book(models.Model):
    book_id = models.CharField(max_length=15, primary_key=True)
    title = models.CharField(max_length=100)
    year_published = models.IntegerField()
    quantity = models.IntegerField(default=0)
    location = models.CharField(max_length=100)
    
    author_id = models.ManyToManyField(Author, related_name='books')
    publisher_id = models.ForeignKey(Publisher, on_delete=models.SET_NULL, related_name='books', null=True)
    category_id = models.ManyToManyField(Category, related_name='books')

    def __str__(self):
        return f'{self.book_id} - {self.title} - {self.location}'


class BorrowBook(models.Model):
    borrower_id = models.ForeignKey(Borrower, on_delete=models.CASCADE, related_name='borrow_table')
    book_id = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrow_table')
    
    def __str__(self):
        return f'Borrower ID: {self.borrower_id} - Book ID: {self.book_id}'


# class BookCategory(models.Model):
#     category_id = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='book_category')
#     book_id = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='book_category')

#     def __str__(self):
#         return f'Category ID: {self.category_id} Book ID: {self.book_id}'


# class BookAuthor(models.Model):
#     author_id = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='book_author')
#     book_id = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='book_author')

#     def __str__(self):
#         return f'Author ID: {self.author_id} Book ID: {self.book_id}'


class BorrowLog(models.Model):
    log_description = models.CharField(max_length=100)
    log_time = models.DateTimeField(default=datetime.now)
    # Either BORROW or RETURN
    activity = models.CharField(max_length=6, default='BORROW')
    book_id = models.ForeignKey(Book, on_delete=models.SET_NULL, related_name='borrow_log', null=True)
    borrower_id = models.ForeignKey(Borrower, on_delete=models.SET_NULL, related_name='borrow_log', null=True)

    def __str__(self):
        return self.log_description

class Admin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.username
