from django.contrib import messages
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.db.models import F
from django.db import transaction 

from .models import Author, Book, Borrower, BorrowLog, Category, Publisher, BorrowBook, BorrowLog, Admin
from .utils import render_borrow_log_to_pdf

import datetime
import calendar
# Decorators
# @gfg_decorator
# def hello_decorator():
#     print("Gfg")

# '''Above code is equivalent to -

# def hello_decorator():
#     print("Gfg")
    
# hello_decorator = gfg_decorator(hello_decorator)'''

# Create your views here.
def index(request):
    """Visitor index page"""
    return render(request, 'lms/index.html', {
        # Navigation show `admin` or `login` depending if session exist or not
        'logged_in': (request.session['logged_in'] if 'logged_in' in request.session
            else False),
    })


def search_book(request):
    """View to search for books"""
    return render(request, 'lms/search-book.html', {
        # Navigation show `admin` or `login` depending if session exist or not
        'logged_in': (request.session['logged_in'] if 'logged_in' in request.session
            else False),
        'books': Book.objects.all(),
    })


def login_admin(request):
    """Admin login view"""
    if request.method == 'POST':
        if Admin.objects.filter(username=request.POST['username'].strip(), 
                                password=request.POST['password']).exists():
            request.session['logged_in'] = True
            return HttpResponseRedirect(reverse('lms:admin-dashboard'))
        else:
            messages.warning(request, 'Invalid username or password')
            return HttpResponseRedirect(reverse('lms:admin-login'))
    
    return render(request, 'lms/admin-login.html')


def check_login(func):
    """Decorator use to validate if admin is login or not
    to prevent unwanted visitor
    """
    def wrapper(*args, **kwargs):
        request = args[0]
        # Prevent random visitor from visiting the page
        if 'logged_in' not in request.session:
            return HttpResponseRedirect(reverse('lms:admin-login'))
        return func(*args, **kwargs)

    return wrapper

@check_login
def admin_dashboard(request):
    """Render dashboard"""
    now = datetime.datetime.now()
    current_month = now.month
    current_year = now.year
    book_count = Book.objects.all().count()
    borrower_count = Borrower.objects.all().count()
    author_count = Author.objects.all().count()
    borrowed_count = BorrowLog.objects.filter(
        activity='BORROW', 
        log_time__month=current_month, 
        log_time__year=current_year
    ).count()
    returned_count = BorrowLog.objects.filter(
        activity='RETURN', 
        log_time__month=current_month, 
        log_time__year=current_year
    ).count()
    return render(request, 'lms/admin/dashboard.html', {
        'dashboard_nav': 'active-nav',
        'book_count': book_count,
        'borrower_count': borrower_count,
        'author_count': author_count,
        'borrowed_count': borrowed_count,
        'returned_count': returned_count,
    })


@check_login
def admin_borrow_return(request):
    """Render borrow or return pages"""
    return render(request, 'lms/admin/borrow-return.html', {
        'borrow_return_nav': 'active-nav',
    })


@check_login
def admin_add_borrow_return(request):
    """Render borrow or return pages"""
    if request.method == 'POST':
        book_id = request.POST['book-id']
        borrower_id = request.POST['borrower-id']
        book = get_object_or_404(Book.objects.select_for_update(), pk=book_id)
        borrower = get_object_or_404(Borrower, pk=int(borrower_id))

        # Check if the book and borrower exist in the borrow book
        # If it exist, then it already borrowed, it follow that borrower must return
        # Else borrow the book
        borrow_book_exist = BorrowBook.objects.select_for_update().filter(book_id=book, borrower_id=borrower_id).exists()
        with transaction.atomic():
            if borrow_book_exist:
                # RETURN LOGIC
                # Delete the book in BorrowBook and log it into BorrowLog
                # Also increase the quantity on the Book table
                
                # Delete the table that represent borrowed book of that value
                borrow_book = get_object_or_404(BorrowBook, book_id=book, borrower_id=borrower)
                borrow_book.delete()

                borrow_log = BorrowLog.objects.create(
                    log_description=f'{borrower.name} returns {book.title}',
                    activity='RETURN',
                    book_id=book,
                    borrower_id=borrower
                )
                # Increase the quantity by 1
                book.quantity = F('quantity') + 1
                book.save()
                return HttpResponseRedirect(reverse('lms:admin-borrow-return'))
            else:
                # BORROW LOGIC
                # Add the book to BorrowBook and log it into BorrowLog
                # Also decrease the quantity on book table
                if not book.quantity <= 0:
                    book.quantity = F('quantity') - 1
                    book.save()
                else:
                    return HttpResponseBadRequest('The current book quantity is zero, fix the quantity first')

                new_borrow_book = BorrowBook.objects.create(
                    book_id=book,
                    borrower_id=borrower
                )
                borrow_log = BorrowLog.objects.create(
                    log_description=f'{borrower.name} borrows {book.title}',
                    activity='BORROW',
                    book_id=book,
                    borrower_id=borrower
                )
                return HttpResponseRedirect(reverse('lms:admin-borrow-return'))
    return HttpResponseRedirect(reverse('lms:admin-borrow-return'))


@check_login
def admin_book(request):
    """Render admin's book view"""
    return render(request, 'lms/admin/book.html', {
        'books': Book.objects.all(),
        'book_nav': 'active-nav',
    })


@check_login
def admin_author(request):
    """Render admin's author view"""
    # Prevent the random visitor to visit admin page
    if 'logged_in' not in request.session:
        return HttpResponseRedirect(reverse('lms:admin-login'))

    return render(request, 'lms/admin/author.html', {
        'authors': Author.objects.all(),
        'author_nav': 'active-nav',
    })


@check_login
def admin_publisher(request):
    """Render admin's publisher view"""
    return render(request, 'lms/admin/publisher.html', {
        'publishers': Publisher.objects.all(),
        'publisher_nav': 'active-nav',
    })


@check_login
def admin_borrower(request):
    """Render admin's borrower view"""
    return render(request, 'lms/admin/borrower.html', {
        'borrowers': Borrower.objects.all(),
        'borrower_nav': 'active-nav'
    })


@check_login
def admin_category(request):
    """Render admin's category view"""
    return render(request, 'lms/admin/category.html', {
        'categories': Category.objects.all(),
        'category_nav': 'active-nav',
    })


@check_login
def admin_borrow_log(request):
    """Render admin's book log view"""
    year_list = BorrowLog.objects.distinct().values_list("log_time__year", flat=True)

    return render(request, 'lms/admin/borrow-log.html', {
        'borrow_logs': BorrowLog.objects.all().order_by('-log_time'),
        'borrow_log_nav': 'active-nav',
        'years': year_list,
    })

@check_login
def admin_borrow_log_with_date(request, month, year):
    """Render admin's book log view with chosen date"""
    year_list = BorrowLog.objects.distinct().values_list("log_time__year", flat=True)

    return render(request, 'lms/admin/borrow-log.html', {
        'borrow_logs': BorrowLog.objects.all()\
            .filter(log_time__month=month, log_time__year=year)\
            .order_by('-log_time'),
        'borrow_log_nav': 'active-nav',
        'month': month,
        'selected_year': year,
        'years': year_list,
    })


@check_login
def admin_borrow_log_pdf(request, month, year):
    """Download the chosen date borrow log pdf"""
    template_name = 'lms/admin/report-borrow.html'
    pdf_name = f'borrow_log {month}_{year}.pdf'
    borrowed_count = BorrowLog.objects.filter(
        activity='BORROW', 
        log_time__month=month, 
        log_time__year=year
    ).count()
    returned_count = BorrowLog.objects.filter(
        activity='RETURN', 
        log_time__month=month, 
        log_time__year=year
    ).count()

    return render_borrow_log_to_pdf(template_name, pdf_name, {
        'borrow_logs': BorrowLog.objects.all()\
            .filter(log_time__month=month, log_time__year=year)\
            .order_by('log_time'),
        'month_name': calendar.month_name[month],
        'year': year,
        'borrow_count': borrowed_count,
        'return_count': returned_count,
    })

@check_login
def admin_logout(request):
    """Run a logout admin logic"""
    # Prevent the random visitor to visit admin page
    if 'logged_in' not in request.session:
        return HttpResponseRedirect(reverse('lms:admin-login'))
    
    try:
        del request.session['logged_in']
    except KeyError:
        pass
    return HttpResponseRedirect(reverse('lms:admin-login'))


def get_or_create_author(author_name):
    """Get or create the author object depending if the author name exist or not"""
    return (
        Author.objects.get(name=author_name) if
        Author.objects.filter(name=author_name).exists() and author_name.strip() != ''
        else Author.objects.create(name=author_name)
    )

def get_or_create_category(category_name):
    """Get or create the category object depending if the category name exist or not"""
    return (
        Category.objects.get(name=category_name) if 
        Category.objects.filter(name=category_name).exists()
        else Category.objects.create(name=category_name)
    )

@check_login
def admin_add_book(request):
    """Add book view and logic"""
    # request.POST.getlist('services')
    if request.method == 'POST':
        book_id = request.POST['id'].strip()
        book_title = request.POST['title'].strip()
        book_year = int(request.POST['year'])
        book_quantity = int(request.POST['quantity'])
        book_location = request.POST['location'].strip()
        book_author = request.POST.getlist('author')
        book_publisher = request.POST['publisher'].strip()
        book_category = request.POST.getlist('category')

        # Create the publisher if not exist, else get it from the database
        if Publisher.objects.filter(name=book_publisher.strip()).exists():
            book_publisher = Publisher.objects.get(name=book_publisher)
        else:
            book_publisher = Publisher.objects.create(name=book_publisher)
        
        # Get or create author depending if it exist or not
        book_author = list(map(get_or_create_author, book_author))
        # Get or create category depending if it exist or not
        book_category = list(map(get_or_create_category, book_category))

        new_book = Book.objects.create(
            book_id=book_id,
            title=book_title,
            year_published=book_year,
            quantity=book_quantity,
            location=book_location,
            publisher_id=book_publisher,
        )
        new_book.save()
        if book_author:
            new_book.author_id.add(*book_author)
        new_book.category_id.add(*book_category)

        return HttpResponseRedirect(reverse('lms:admin-book'))
    
    return render(request, 'lms/admin/book-add.html', {
        'authors': Author.objects.all(),
        'publishers': Publisher.objects.all(),
        'categories': Category.objects.all(),
    })


@check_login
def admin_update_book(request, book_id):
    """Update book view and logic"""
    # Get the wanted book
    if request.method == 'POST':
        book = get_object_or_404(Book.objects.select_for_update(), pk=book_id)  # Book.objects.get(pk=book_id)
        with transaction.atomic():
            new_book_id = request.POST['id'].strip()
            new_book_title = request.POST['title'].strip()
            new_book_year_published = int(request.POST['year'])
            new_book_quantity = int(request.POST['quantity'])
            new_book_location = request.POST['location'].strip()
            new_book_author = request.POST.getlist('author')
            new_book_publisher = request.POST['publisher']
            new_book_category = request.POST.getlist('category')

            # Create the publisher if not exist, else get it from the database
            if Publisher.objects.filter(name=new_book_publisher.strip()).exists():
                new_book_publisher = Publisher.objects.get(name=new_book_publisher)
            else:
                new_book_publisher = Publisher.objects.create(name=new_book_publisher)

            # Get or create author depending if it exist or not
            new_book_author = list(map(get_or_create_author, new_book_author))
            # Get or create category depending if it exist or not
            new_book_category = list(map(get_or_create_category, new_book_category))

            book.book_id = new_book_id
            book.title = new_book_title
            book.year_published = new_book_year_published
            book.quantity = new_book_quantity
            book.location = new_book_location
            book.publisher_id = new_book_publisher
            book.author_id.set(new_book_author)
            book.category_id.set(new_book_category)
            book.save()

            return HttpResponseRedirect(reverse('lms:admin-book'))

    book = get_object_or_404(Book, pk=book_id)
    exclude_category = list(book.category_id.values_list('name', flat=True))
    exclude_author = list(book.author_id.values_list('name', flat=True))

    category = Category.objects.exclude(name__in=exclude_category)
    author = Author.objects.exclude(name__in=exclude_author)
    publisher = book.publisher_id

    return render(request, 'lms/admin/book-update.html', {
        'book': book,
        'categories': category,
        'authors': author,
        'publisher': publisher,
    })


@check_login
def admin_delete_book(request, book_id):
    """Delete book view and logic"""
    # Get the wanted author
    book = get_object_or_404(Book, pk=book_id) # Book.objects.get(pk=book_id)

    # Delete it
    book.delete()
    return HttpResponseRedirect(reverse('lms:admin-book'))


@check_login
def admin_add_borrower(request):
    """Add borrower view and logic"""
    if request.method == 'POST':
        borrower_name = request.POST['name']
        borrower_address = request.POST['address']
        borrower_contact = request.POST['contact']
        new_borrower = Borrower.objects.create(
            name=borrower_name, 
            address=borrower_address, 
            contact=borrower_contact,
        )
        new_borrower.save()
        return HttpResponseRedirect(reverse('lms:admin-borrower'))
        
    return render(request, 'lms/admin/borrower-add.html')


@check_login
def admin_update_borrower(request, borrower_id):
    """Update borrower view and logic"""
    # Get the wanted borrower
    borrower = Borrower.objects.get(pk=borrower_id)
    if request.method == 'POST':
        new_borrower_name = request.POST['name']
        new_borrower_address = request.POST['address']
        new_borrower_contact = request.POST['contact']
        borrower.name = new_borrower_name
        borrower.address = new_borrower_address
        borrower.contact = new_borrower_contact
        borrower.save()
        return HttpResponseRedirect(reverse('lms:admin-borrower'))
    return render(request, 'lms/admin/borrower-update.html', {
        'borrower': borrower,
    })


@check_login
def admin_delete_borrower(request, borrower_id):
    """Delete borrower view and logic"""
    # Get the wanted author
    borrower = Borrower.objects.get(pk=borrower_id)

    # Delete it
    borrower.delete()
    return HttpResponseRedirect(reverse('lms:admin-borrower'))


@check_login
def admin_member_card(request, borrower_id):
    """Delete borrower view and logic"""
    # Get the wanted author
    borrower = Borrower.objects.get(pk=borrower_id)

    return render(request, 'lms/admin/member-card.html', {
        'borrower': borrower,
        'qr_text': 'card' + str(borrower.borrower_id)
    })


@check_login
def admin_add_author(request):
    """Add author view and logic"""
    if request.method == 'POST':
        author_name = request.POST['name']
        new_author = Author.objects.create(name=author_name)
        new_author.save()
        return HttpResponseRedirect(reverse('lms:admin-author'))
        
    return render(request, 'lms/admin/author-add.html')


@check_login
def admin_update_author(request, author_id):
    """Update author view and logic"""
    # Get the wanted author
    author = Author.objects.get(pk=author_id)
    if request.method == 'POST':
        new_author_name = request.POST['name']
        author.name = new_author_name
        author.save()
        return HttpResponseRedirect(reverse('lms:admin-author'))
    return render(request, 'lms/admin/author-update.html', {
        'author': author,
    })


@check_login
def admin_delete_author(request, author_id):
    """Delete author view and logic"""
    # Get the wanted author
    author = Author.objects.get(pk=author_id)

    # Delete it
    author.delete()
    return HttpResponseRedirect(reverse('lms:admin-author'))


@check_login
def admin_add_publisher(request): 
    """Add publisher view and logic"""
    if request.method == 'POST':
        publisher_name = request.POST['name']
        new_publisher = Publisher.objects.create(name=publisher_name)
        new_publisher.save()
        return HttpResponseRedirect(reverse('lms:admin-publisher'))
    return render(request, 'lms/admin/publisher-add.html')


@check_login
def admin_update_publisher(request, publisher_id):
    """Update publisher view and logic"""
    # Get the wanted author
    publisher = Publisher.objects.get(pk=publisher_id)
    if request.method == 'POST':
        new_publisher_name = request.POST['name']
        publisher.name = new_publisher_name
        publisher.save()
        return HttpResponseRedirect(reverse('lms:admin-publisher'))
    return render(request, 'lms/admin/publisher-update.html', {
        'publisher': publisher,
    })


@check_login
def admin_delete_publisher(request, publisher_id):
    """Delete publisher view and logic"""
    # Get the wanted author
    publisher = Publisher.objects.get(pk=publisher_id)

    # Delete it
    publisher.delete()
    return HttpResponseRedirect(reverse('lms:admin-publisher'))

@check_login
def admin_add_category(request): 
    """Add category view and logic"""
    if request.method == 'POST':
        category_name = request.POST['name']
        new_category = Category.objects.create(name=category_name)
        new_category.save()
        return HttpResponseRedirect(reverse('lms:admin-category'))
    return render(request, 'lms/admin/category-add.html')


@check_login
def admin_update_category(request, category_id):
    """Update category view and logic"""
    # Get the wanted author
    category = Category.objects.get(pk=category_id)
    if request.method == 'POST':
        new_category_name = request.POST['name']
        category.name = new_category_name
        category.save()
        return HttpResponseRedirect(reverse('lms:admin-category'))
    return render(request, 'lms/admin/category-update.html', {
        'category': category,
    })


@check_login
def admin_delete_category(request, category_id):
    """Delete category view and logic"""
    # Get the wanted author
    category = Category.objects.get(pk=category_id)

    # Delete it
    category.delete()
    return HttpResponseRedirect(reverse('lms:admin-category'))


@check_login
def admin_delete_borrow_log(request, id):
    """Delete category view and logic"""
    # Get the wanted author
    borrow_log = BorrowLog.objects.get(pk=id)

    # Delete it
    borrow_log.delete()
    return HttpResponseRedirect(reverse('lms:admin-borrow-log'))


@check_login
def admin_book_detail(request, book_id):
    """Render the book details page"""
    book = Book.objects.get(pk=book_id)
    return render(request, 'lms/admin/book-detail.html', {
        'book': book,
    })


@check_login
def admin_borrower_detail(request, borrower_id):
    """Render the borrower details page"""
    borrower = Borrower.objects.get(pk=borrower_id)
    return render(request, 'lms/admin/borrower-detail.html', {
        'borrower': borrower,
    })


@check_login
def admin_author_detail(request, author_id):
    """Render the borrower details page"""
    author = Author.objects.get(pk=author_id)
    return render(request, 'lms/admin/author-detail.html', {
        'author': author,
    })


@check_login
def admin_publisher_detail(request, publisher_id):
    """Render the publisher details page"""
    publisher = Publisher.objects.get(pk=publisher_id)
    return render(request, 'lms/admin/publisher-detail.html', {
        'publisher': publisher,
    })