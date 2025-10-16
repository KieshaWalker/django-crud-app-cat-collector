# Cat Collector - Django Tutorial

A comprehensive step-by-step guide to building a full-stack Django web application with user authentication, CRUD operations, and modern UI design.

## 🎯 Project Overview

**Cat Collector** is a web application that allows users to:
- Create accounts and log in/out
- Add, view, edit, and delete their cats
- Track feeding schedules for each cat
- Manage their toy collection
- View personalized dashboards

## 📋 Prerequisites

Before starting, ensure you have:
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment knowledge (we'll use pipenv)
- Basic HTML/CSS knowledge
- Command line familiarity

## 🚀 Step-by-Step Tutorial

### Step 1: Project Setup

#### 1.1 Create Project Directory
```bash
mkdir cat-collector-tutorial
cd cat-collector-tutorial
```

#### 1.2 Set Up Virtual Environment
```bash
# Install pipenv if you don't have it
pip install pipenv

# Create virtual environment and install Django
pipenv install django python-dotenv psycopg2-binary

# Activate virtual environment
pipenv shell
```

#### 1.3 Create Django Project
```bash
# Create Django project
django-admin startproject catcollector .

# Create main app
python manage.py startapp main_app
```

#### 1.4 Configure Settings
Edit `catcollector/settings.py`:

```python
# Add to INSTALLED_APPS
INSTALLED_APPS = [
    'main_app',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# Database configuration (we'll use PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'catcollector',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Static files
STATIC_URL = 'static/'

# Authentication redirects
LOGIN_REDIRECT_URL = 'cat-index'
LOGOUT_REDIRECT_URL = 'home'
LOGIN_URL = 'home'
```

### Step 2: Database Models

#### 2.1 Create Models
Edit `main_app/models.py`:

```python
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

# Constants
MEALS = (
    ('B', 'Breakfast'),
    ('L', 'Lunch'),
    ('D', 'Dinner')
)

class Cat(models.Model):
    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100)
    description = models.TextField(max_length=250)
    age = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    toys = models.ManyToManyField('Toy')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('cat-detail', kwargs={'cat_id': self.id})

class Feeding(models.Model):
    date = models.DateField()
    meal = models.CharField(
        max_length=1,
        choices=MEALS,
        default=MEALS[0][0]
    )
    cat = models.ForeignKey(Cat, on_delete=models.CASCADE, related_name='feedings')

    def __str__(self):
        return f"{self.get_meal_display()} on {self.date}"

    class Meta:
        ordering = ['-date']

class Toy(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('toy-detail', kwargs={'pk': self.id})
```

#### 2.2 Register Models in Admin
Edit `main_app/admin.py`:

```python
from django.contrib import admin
from .models import Cat, Feeding, Toy

admin.site.register(Cat)
admin.site.register(Feeding)
admin.site.register(Toy)
```

#### 2.3 Create and Run Migrations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Step 3: Views and URL Configuration

#### 3.1 Create Views
Edit `main_app/views.py`:

```python
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from .models import Cat, Feeding, Toy
from .forms import FeedingForm

# Authentication Views
class Home(LoginView):
    template_name = 'home.html'

def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('cat-index')
        else:
            error_message = 'Invalid sign up - try again'
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'signup.html', context)

# Cat Views
@login_required
def cat_index(request):
    cats = Cat.objects.filter(user=request.user)
    return render(request, 'cats/index.html', {'cats': cats})

@login_required
def cat_detail(request, cat_id):
    cat = Cat.objects.get(id=cat_id, user=request.user)
    feeding_form = FeedingForm()
    return render(request, 'cats/detail.html', {
        'cat': cat, 'feeding_form': feeding_form,
    })

@login_required
def add_feeding(request, cat_id):
    cat = Cat.objects.get(id=cat_id, user=request.user)
    form = FeedingForm(request.POST)
    if form.is_valid():
        new_feeding = form.save(commit=False)
        new_feeding.cat_id = cat_id
        new_feeding.save()
    return redirect('cat-detail', cat_id=cat_id)

class CatCreate(LoginRequiredMixin, CreateView):
    model = Cat
    fields = ['name', 'breed', 'description', 'age']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class CatUpdate(LoginRequiredMixin, UpdateView):
    model = Cat
    fields = ['breed', 'description', 'age']

class CatDelete(LoginRequiredMixin, DeleteView):
    model = Cat
    success_url = '/cats/'

# Toy Views
@login_required
def toy_detail(request, pk):
    toy = Toy.objects.get(id=pk)
    return render(request, 'main_app/toy_detail.html', {'toy': toy})

class ToyCreate(LoginRequiredMixin, CreateView):
    model = Toy
    fields = '__all__'

class ToyList(LoginRequiredMixin, ListView):
    model = Toy

class ToyDetail(LoginRequiredMixin, DetailView):
    model = Toy

class ToyUpdate(LoginRequiredMixin, UpdateView):
    model = Toy
    fields = ['name', 'color']

class ToyDelete(LoginRequiredMixin, DeleteView):
    model = Toy
    success_url = '/toys/'
```

#### 3.2 Create Forms
Create `main_app/forms.py`:

```python
from django import forms
from .models import Feeding

class FeedingForm(forms.ModelForm):
    class Meta:
        model = Feeding
        fields = ['date', 'meal']
        widgets = {
            'date': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={
                    'placeholder': 'Select a date',
                    'type': 'date'
                }
            ),
        }
```

#### 3.3 Configure URLs
Edit `main_app/urls.py`:

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('about/', views.about, name='about'),
    path('cats/', views.cat_index, name='cat-index'),
    path('cats/<int:cat_id>/', views.cat_detail, name='cat-detail'),
    path('cats/create/', views.CatCreate.as_view(), name='cat-create'),
    path('cats/<int:pk>/update/', views.CatUpdate.as_view(), name='cat-update'),
    path('cats/<int:pk>/delete/', views.CatDelete.as_view(), name='cat-delete'),
    path('cats/<int:cat_id>/add_feeding/', views.add_feeding, name='add_feeding'),
    path('toys/create/', views.ToyCreate.as_view(), name='toy-create'),
    path('toys/<int:pk>/', views.toy_detail, name='toy-detail'),
    path('toys/', views.ToyList.as_view(), name='toy-index'),
    path('toys/<int:pk>/update/', views.ToyUpdate.as_view(), name='toy-update'),
    path('toys/<int:pk>/delete/', views.ToyDelete.as_view(), name='toy-delete'),
    path('accounts/signup/', views.signup, name='signup'),
]
```

Edit `catcollector/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main_app.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]
```

### Step 4: Templates and Static Files

#### 4.1 Base Template
Create `main_app/templates/base.html`:

```html
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Cat Collector</title>
  <link rel="stylesheet" href="{% static 'css/base.css' %}">
</head>
<body>
  <header>
    <div class="header-content">
      <a href="{% url 'home' %}">
        <div class="logo">
          <img src="{% static 'images/logotype.svg' %}" alt="Cat Collector Logo" />
        </div>
      </a>
      <nav>
        <ul>
          {% if user.is_authenticated %}
            <li><a href="{% url 'cat-index' %}">All Cats</a></li>
            <li><a href="{% url 'toy-index' %}">All Toys</a></li>
            <li><a href="{% url 'cat-create' %}">Add a Cat</a></li>
            <li><a href="{% url 'toy-create' %}">Add a Toy</a></li>
            <li><a href="{% url 'about' %}">About</a></li>
            <li>
              <form id="logout-form" method="post" action="{% url 'logout' %}">
                {% csrf_token %}
                <button type="submit">Log out</button>
              </form>
            </li>
          {% else %}
            <li><a href="{% url 'about' %}">About</a></li>
            <li><a href="{% url 'home' %}">Login</a></li>
            <li><a href="{% url 'signup' %}">Sign Up</a></li>
          {% endif %}
        </ul>
      </nav>
    </div>
  </header>

  <main>
    {% block content %}
    {% endblock %}
  </main>

  <footer>
    <p>&copy; 2025 Cat Collector</p>
  </footer>
</body>
</html>
```

#### 4.2 Home Template
Create `main_app/templates/home.html`:

```html
{% extends 'base.html' %}
{% load static %}
{% block head %}
<link rel="stylesheet" href="{% static 'css/home.css' %}" />
{% endblock %}
{% block content %}

<section class="logo-container">
  <div class="cat-container">
    <img src="{% static 'images/splash.svg' %}" alt="The Cat Collector Cat" />
  </div>
  <img src="{% static 'images/logotype.svg' %}" alt="Text reads: Cat Collector" />
</section>

{% if not user.is_authenticated %}
<section>
  <form action="{% url 'home' %}" method="post" class="login">
    <h1>Login</h1>
    {% csrf_token %}
    {{ form.as_p }}
    <input type="hidden" name="next" value="{{ next }}" />
    <button type="submit" class="btn submit">Login</button>
  </form>
</section>
{% endif %}

{% endblock %}
```

#### 4.3 Signup Template
Create `main_app/templates/signup.html`:

```html
{% extends 'base.html' %}
{% load static %}
{% block head %}
<link rel="stylesheet" href="{% static 'css/form.css' %}" />
{% endblock %}
{% block content %}
<div class="page-header">
  <h1>Sign Up</h1>
  <img src="{% static 'images/nerd-cat.svg' %}" alt="A cat using a computer" />
</div>
{% if error_message %}
  <p class="red-text">{{ error_message }}</p>
{% endif %}
<form action="" method="post" class="form-container" autocomplete="off">
  {% csrf_token %}
  <table>
    {{ form.as_table }}
  </table>
  <button type="submit" class="btn submit">Submit!</button>
</form>
{% endblock %}
```

#### 4.4 Cat Templates
Create `main_app/templates/cats/index.html`:

```html
{% extends 'base.html' %}
{% load static %}
{% block head %}
<link rel="stylesheet" href="{% static 'css/cats/cat-index.css' %}" />
{% endblock %}
{% block content %}

<section class="page-header">
  <h1>Cat List</h1>
  <img src="{% static 'images/cool-cat.svg' %}" alt="A cool cat" />
  <img src="{% static 'images/happy-cat.svg' %}" alt="A happy cat" />
  <img src="{% static 'images/teacup-cat.svg' %}" alt="A cat in a teacup" />
  <img src="{% static 'images/cat-in-box.svg' %}" alt="A cat in a box" />
</section>

<section class="card-container">
  {% for cat in cats %}
  <div class="card">
    <a href="{% url 'cat-detail' cat.id %}">
      <div class="card-content">
        <div class="card-img-container">
          <img src="{% static 'images/sk8r-boi-cat.svg' %}" alt="A skater boy cat" />
        </div>
        <h2 class="card-title">{{ cat.name }}</h2>
        {% if cat.age > 0 %}
        <p>A {{ cat.age }} year old {{ cat.breed }}</p>
        {% else %}
        <p>A {{ cat.breed }} kitten.</p>
        {% endif %}
        <p><small>{{ cat.description }}</small></p>
      </div>
    </a>
  </div>
  {% endfor %}
</section>

{% endblock %}
```

Create `main_app/templates/cats/detail.html`:

```html
{% extends 'base.html' %}
{% load static %}
{% block head %}
<link rel="stylesheet" href="{% static 'css/cats/cat-detail.css' %}" />
{% endblock %}
{% block content %}
<section class="cat-container">
  <div class="cat-img">
    <img src="{% static 'images/sk8r-boi-cat.svg' %}" alt="A skater boy cat" />
  </div>
  <div class="cat-details">
    <h1>{{ cat.name }}</h1>
    {% if cat.age > 0 %}
      <h2>A {{ cat.age }} year old {{ cat.breed }}</h2>
    {% else %}
      <h2>A {{ cat.breed }} kitten.</h2>
    {% endif %}
    <p>{{ cat.description }}</p>

    <div class="cat-actions">
      <a href="{% url 'cat-update' cat.id %}" class="btn warn">Edit</a>
      <a href="{% url 'cat-delete' cat.id %}" class="btn danger">Delete</a>
    </div>
  </div>
</section>

<div class="feedings-toy-container">
  <section class="feedings">
    <div class="subsection-title">
      <h2>Feedings</h2>
      <img src="{% static 'images/cat-cone.svg' %}" alt="An ice cream cone cat" />
      <img src="{% static 'images/cat-onigiri.svg' %}" alt="A cat as onigiri" />
      <img src="{% static 'images/kitty-kabob.svg' %}" alt="A kabob of kittens" />
    </div>

    <form action="{% url 'add_feeding' cat.id %}" method="post" class="subsection-content" autocomplete="off">
      {% csrf_token %}
      {{ feeding_form.as_p }}
      <button type="submit" class="btn submit">Add Feeding</button>
    </form>

    <h3>Past Feedings</h3>
    {% if cat.feedings.all.count %}
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Meal</th>
          </tr>
        </thead>
        <tbody>
          {% for feeding in cat.feedings.all %}
          <tr>
            <td>{{ feeding.date }}</td>
            <td>{{ feeding.get_meal_display }}</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    {% else %}
      <div class="subsection-content">
        <p>⚠️ {{ cat.name }} has not been fed!</p>
      </div>
    {% endif %}
  </section>
</div>
{% endblock %}
```

#### 4.5 Form Templates
Create `main_app/templates/main_app/cat_form.html`:

```html
{% extends 'base.html' %}
{% load static %}
{% block head %}
<link rel="stylesheet" href="{% static 'css/form.css' %}" />
{% endblock %}
{% block content %}

<div class="page-header">
  {% if object %}
    <h1>Edit {{ object.name }}</h1>
  {% else %}
    <h1>Add a Cat</h1>
  {% endif %}
  <img src="{% static 'images/nerd-cat.svg' %}" alt="A cat using a computer" />
</div>

<form action="" method="post" class="form-container">
  {% csrf_token %}
  <table>
    {{ form.as_table }}
  </table>
  <button type="submit" class="btn submit">Submit!</button>
</form>

{% endblock %}
```

Create `main_app/templates/main_app/cat_confirm_delete.html`:

```html
{% extends 'base.html' %}
{% load static %}
{% block content %}

<div class="page-header">
  <h1>Delete Cat?</h1>
  <img src="{% static 'images/nerd-cat.svg' %}" alt="A cat using a computer" />
</div>

<h2>Are you sure you want to delete {{ cat.name }}?</h2>

<form action="" method="post" class="form">
  {% csrf_token %}
  <a href="{% url 'cat-detail' cat.id %}" class="btn secondary">Cancel</a>
  <button type="submit" class="btn danger">Yes - Delete!</button>
</form>

{% endblock %}
```

Create `main_app/templates/main_app/toy_detail.html`:

```html
{% extends 'base.html' %}
{% load static %}
{% block head %}
<link rel="stylesheet" href="{% static 'css/cats/cat-detail.css' %}" />
{% endblock %}
{% block content %}
<section class="cat-container">
  <div class="cat-img">
    <img src="{% static 'images/sk8r-boi-cat.svg' %}" alt="A skater boy cat" />
  </div>
  <div class="cat-details">
    <h1>{{ toy.name }}</h1>
    <h2>{{ toy.color }} toy</h2>
    <div class="cat-actions">
      <a href="#" class="btn warn">Edit</a>
      <a href="#" class="btn danger">Delete</a>
    </div>
  </div>
</section>
{% endblock %}
```

#### 4.6 About Template
Create `main_app/templates/about.html`:

```html
{% extends 'base.html' %}

{% block content %}
<div class="page-header">
  <h1>About the Cat Collector</h1>
  <img src="{% static 'images/nerd-cat.svg' %}" alt="A cat using a computer" />
</div>

<p>Welcome to Cat Collector, the ultimate app for cat lovers! Here you can:</p>
<ul>
  <li>Keep track of all your feline friends</li>
  <li>Record feeding schedules</li>
  <li>Manage your toy collection</li>
  <li>Share your cat collection with other users</li>
</ul>
{% endblock %}
```

### Step 5: Static Files and Styling

#### 5.1 Create Static Directory Structure
```bash
mkdir -p main_app/static/css/cats
mkdir -p main_app/static/images
```

#### 5.2 CSS Files
Create `main_app/static/css/base.css`:

```css
/* CSS Variables */
:root {
  --primary: rgb(26, 128, 0);
  --secondary: rgb(57, 57, 57);
  --warn: rgb(255, 102, 0);
  --danger: rgb(220, 20, 30);
  --text-color: rgb(57, 57, 57);
  --link-hover-color: rgb(26, 128, 0);
  --card-box-shadow: 5px 5px 6px -1px #aaa;
  --font-xl: 2.4rem;
  --font-l: 1.8rem;
  --font-reg: 1.6rem;
  --card-border-radius: 6px;
}

/* Base Styles */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Helvetica Neue', sans-serif;
  line-height: 1.6;
  color: var(--text-color);
}

h1, h2, h3 {
  margin-bottom: 1rem;
}

a {
  color: var(--primary);
  text-decoration: none;
}

a:hover {
  color: var(--link-hover-color);
}

/* Header */
header {
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo img {
  height: 40px;
}

nav ul {
  display: flex;
  list-style: none;
  gap: 2rem;
}

nav a {
  font-weight: 600;
}

/* Main Content */
main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

/* Buttons */
.btn {
  display: inline-block;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  text-decoration: none;
  transition: background-color 0.3s;
}

.btn.submit {
  background: var(--primary);
  color: white;
}

.btn.warn {
  background: var(--warn);
  color: white;
}

.btn.danger {
  background: var(--danger);
  color: white;
}

.btn.secondary {
  background: var(--secondary);
  color: white;
}

/* Logout Form */
#logout-form button {
  text-decoration: none;
  color: var(--text-color);
  font-weight: 600;
  font-size: 16px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  font-family: inherit;
}

#logout-form button:hover {
  color: var(--link-hover-color);
}

/* Footer */
footer {
  background: var(--secondary);
  color: white;
  text-align: center;
  padding: 1rem;
  margin-top: 4rem;
}
```

Create `main_app/static/css/home.css`:

```css
.logo-container {
  text-align: center;
  margin: 4rem 0;
}

.cat-container img {
  width: 200px;
  height: auto;
}

.logotype {
  margin-top: 2rem;
  width: 300px;
  height: auto;
}

.login {
  max-width: 400px;
  margin: 0 auto;
  padding: 2rem;
  border: 1px solid #ddd;
  border-radius: var(--card-border-radius);
}

.login h1 {
  text-align: center;
  margin-bottom: 2rem;
}

.login label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.login input {
  width: 100%;
  padding: 0.5rem;
  margin-bottom: 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}
```

Create `main_app/static/css/form.css`:

```css
.page-header {
  text-align: center;
  margin-bottom: 3rem;
}

.page-header img {
  width: 100px;
  height: auto;
  margin-top: 1rem;
}

.form-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem;
  border: 1px solid #ddd;
  border-radius: var(--card-border-radius);
}

.form-container table {
  width: 100%;
}

.form-container td {
  padding: 0.5rem 0;
}

.form-container input,
.form-container textarea,
.form-container select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.red-text {
  color: var(--danger);
  text-align: center;
  margin-bottom: 1rem;
}
```

#### 5.3 Add Images
You'll need to add SVG images to `main_app/static/images/`:
- `splash.svg` - Main cat logo
- `logotype.svg` - Text logo
- `nerd-cat.svg` - Cat with computer
- `sk8r-boi-cat.svg` - Skateboard cat
- Various other cat SVG icons

### Step 6: Testing and Deployment

#### 6.1 Run the Application
```bash
# Activate virtual environment
pipenv shell

# Run development server
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` to see your app!

#### 6.2 Test All Features
1. **Sign up** for a new account
2. **Log in** with your credentials
3. **Add cats** using the "Add a Cat" link
4. **View cat details** and add feedings
5. **Edit and delete** cats
6. **Add toys** and view the toy collection
7. **Log out** and verify you can't access protected pages

#### 6.3 Environment Configuration
Create a `.env` file in your project root:

```bash
# .env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/catcollector
```

Update `settings.py` to use environment variables:

```python
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
```

#### 6.4 Deployment Considerations
- Set `DEBUG = False` in production
- Use a production database (PostgreSQL recommended)
- Configure static file serving
- Set up proper logging
- Use environment variables for secrets
- Consider using services like Heroku, DigitalOcean, or AWS

#### 5.2 Images
Add SVG images for the UI.

### Step 6: Testing and Deployment

#### 6.1 Run the Application
```bash
python manage.py runserver
```

#### 6.2 Test All Features
- User registration and login
- CRUD operations for cats
- Feeding tracking
- Toy management

#### 6.3 Deployment Considerations
- Environment variables
- Static file serving
- Database configuration

## 📚 Key Concepts Covered

### Django Fundamentals
- Project structure
- Apps and models
- Views (function-based and class-based)
- Templates and static files
- URL configuration
- Forms and validation

### Authentication & Authorization
- User model and registration
- Login/logout functionality
- Session management
- Protected views
- User-specific data

### Database Design
- Models and relationships
- Migrations
- Foreign keys and many-to-many relationships
- Data integrity

### Frontend Development
- HTML templates
- CSS styling
- Responsive design
- User experience considerations

## 🎯 Learning Objectives

By the end of this tutorial, you will understand:
- How to structure a Django project
- Implementing user authentication
- Creating CRUD operations
- Building responsive web interfaces
- Database modeling and relationships
- Best practices for Django development

## 🚀 Next Steps & Extensions

### Beginner Extensions
- Add cat photos (image uploads)
- Implement feeding reminders
- Add cat age validation
- Create user profiles

### Intermediate Extensions
- Add search and filtering
- Implement pagination
- Add social features (sharing cats)
- Create API endpoints with Django REST Framework

### Advanced Extensions
- Add real-time notifications
- Implement background tasks (Celery)
- Add comprehensive testing
- Deploy with Docker

## 🐛 Troubleshooting

### Common Issues

**Migration Errors**
```bash
# Reset migrations if needed
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
rm db.sqlite3
python manage.py makemigrations
python manage.py migrate
```

**Template Not Found**
- Check template directory structure
- Verify template names match view expectations
- Ensure `TEMPLATES` setting includes your app directories

**Static Files Not Loading**
- Run `python manage.py collectstatic` for production
- Check `STATIC_URL` and `STATICFILES_DIRS` settings

**Authentication Issues**
- Verify `LOGIN_URL` and redirect settings
- Check that `@login_required` decorators are applied
- Ensure user model relationships are correct

## 📖 Additional Resources

- [Django Official Documentation](https://docs.djangoproject.com/)
- [Django Girls Tutorial](https://tutorial.djangogirls.org/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Django Packages](https://djangopackages.org/)

URL Request → URL Pattern → View → Model Query → Template → HTML Response
                      ↓
                   Form Processing


class Cat(models.Model):
    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

@login_required
def cat_detail(request, cat_id):
    cat = Cat.objects.get(id=cat_id, user=request.user)
    feeding_form = FeedingForm()
    return render(request, 'cats/detail.html', {
        'cat': cat, 'feeding_form': feeding_form,
    })

<h1>{{ cat.name }}</h1>
<h2>A {{ cat.age }} year old {{ cat.breed }}</h2>

path('cats/<int:cat_id>/', views.cat_detail, name='cat-detail'),


. Identify Template Context Variables
Look for {{ variable }} in templates to understand what data the view passes:

<!-- In cats/detail.html -->
<h1>{{ cat.name }}</h1>  <!-- cat object passed from view -->
{{ feeding_form }}      <!-- form instance passed from view -->

2. Check Template Tags and Filters
{% for feeding in cat.feedings.all %}  <!-- Loop through related data -->
{% if cat.age > 0 %}                   <!-- Conditional rendering -->
{% url 'cat-detail' cat.id %}          <!-- URL reversal -->
3. Examine Form Rendering
<form action="{% url 'add_feeding' cat.id %}" method="post">
  {% csrf_token %}
  {{ feeding_form.as_p }}  <!-- Renders form fields -->
</form>
4. Look for Static File References
<link rel="stylesheet" href="{% static 'css/base.css' %}">
<img src="{% static 'images/cat.svg' %}" alt="Cat">

For /cats/1/ (viewing cat details):

URL Pattern: path('cats/<int:cat_id>/', views.cat_detail, name='cat-detail')
View Function: cat_detail(request, cat_id) queries Cat.objects.get(id=cat_id)
Template Context: Passes {'cat': cat, 'feeding_form': feeding_form}
Template Rendering: cats/detail.html displays {{ cat.name }}, {{ cat.breed }}, etc.
Form Handling: FeedingForm for adding feeding 


pipenv install django-debug-toolbar

if DEBUG:
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    
    # For Docker/local development
    INTERNAL_IPS = ['127.0.0.1', 'localhost']    if DEBUG:
        INSTALLED_APPS.append('debug_toolbar')
        MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
        
        # For Docker/local development
        INTERNAL_IPS = ['127.0.0.1', 'localhost']

What it gives you:

SQL queries with execution time
Template context variables
Request/response headers
Cache usage
Signals fired
Settings values

3. Print Statements & Logging (Quick & Dirty)
import logging
logger = logging.getLogger(__name__)

def cat_detail(request, cat_id):
    logger.debug(f"Cat ID received: {cat_id}")
    logger.debug(f"User: {request.user}")
    cat = Cat.objects.get(id=cat_id, user=request.user)
    logger.debug(f"Cat found: {cat.name}")
    # ... rest of view

In templates (temporary):

<!-- Debug template variables -->
<pre>{{ cat|json_script:"cat-data" }}</pre>
<script>
  console.log(JSON.parse(document.getElementById('cat-data').textContent));
</script>

4. Database Debugging
# In view or shell
from django.db import connection
print(connection.queries)  # Shows all SQL queries executed

Django shell for data inspection:


from main_app.models import Cat
cats = Cat.objects.filter(user__username='testuser')
print(cats.query)  # See generated SQL
for cat in cats:
    print(f"{cat.name}: {cat.feedings.count()} feedings")


5. Template Debugging
<!-- At top of template -->
{% load static %}
<!-- Debug all context variables -->
{% for key, value in request.GET.items %}
  <p>GET {{ key }}: {{ value }}</p>
{% endfor %}

<!-- Debug specific objects -->
<pre>Cat: {{ cat|json_script:"cat-debug" }}</pre>


6. Form Debugging
def add_feeding(request, cat_id):
    form = FeedingForm(request.POST)
    if form.is_valid():
        # Form is valid
        print("Form is valid")
        print(form.cleaned_data)
    else:
        # Form has errors
        print("Form errors:", form.errors)
        print("Non-field errors:", form.non_field_errors())
    # ... rest of view


7. URL & View Debugging
# In urls.py - add temporary debug
from django.urls import path, include
from django.http import HttpResponse

def debug_url(request, **kwargs):
    return HttpResponse(f"URL matched! kwargs: {kwargs}")

# Temporarily replace a pattern
path('cats/<int:cat_id>/', debug_url, name='cat-detail'),


10. Common Issues & Quick Fixes
Template not loading: Check TEMPLATE_DIRS in settings
Static files not loading: Run python [manage.py](http://_vscodecontentref_/2) collectstatic
Database errors: Check python [manage.py](http://_vscodecontentref_/3) dbshell
Permission errors: Verify user authentication and object ownership


11. Testing During Development
Quick model testing:
python manage.py shell
from main_app.models import Cat, User
user = User.objects.create_user('test', 'test@test.com', 'pass')
cat = Cat.objects.create(name='Test', breed='Tabby', user=user)
print(cat.feedings.all())  # Test relationships


View testing:
from django.test import Client
client = Client()
response = client.get('/cats/')
print(response.status_code)
print(response.content.decode())


PostgreSQL Setup & Configuration
# Start PostgreSQL shell
psql postgres

# Create database and user
CREATE DATABASE catcollector;
CREATE USER catcollector_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE catcollector TO catcollector_user;
ALTER USER catcollector_user CREATEDB;
\q

test connection : 
psql -d catcollector -U catcollector_user -h localhost

3. Django-PostgreSQL Configuration

pipenv install psycopg2-binary


Update settings.py:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'catcollector',
        'USER': 'catcollector_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

For production (with environment variables):

import os
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}


1. Model-Database Synchronization
Check migration status:
python manage.py showmigrations
Apply migrations:
python manage.py migrate
Create migrations for model changes:
python manage.py makemigrations
python manage.py migrate
Check for migration issues:
python manage.py check

2. Route-Model Consistency
# In urls.py - ensure patterns match view signatures
path('cats/<int:cat_id>/', views.cat_detail, name='cat-detail'),
# View must accept: def cat_detail(request, cat_id):

Test URL resolution:

from django.urls import reverse
from django.test import Client

client = Client()
# Test if URL resolves correctly
response = client.get(reverse('cat-detail', kwargs={'cat_id': 1}))
print(response.status_code)

3. Database Schema Verification
psql -d catcollector -U catcollector_user
\d main_app_cat;  -- Show table structure
\dt;              -- List all tables

Compare with Django models:

python manage.py dbshell
# Then run: \d main_app_cat

ostgreSQL Debugging Techniques
1. Connection Debugging
Test database connection:

from django.db import connection
try:
    cursor = connection.cursor()
    cursor.execute("SELECT 1")
    print("Database connection successful")
except Exception as e:
    print(f"Database connection failed: {e}")

Check connection settings:

from django.conf import settings
db_settings = settings.DATABASES['default']
print(f"Engine: {db_settings['ENGINE']}")
print(f"Name: {db_settings['NAME']}")
print(f"Host: {db_settings['HOST']}")

2. Query Debugging
Enable SQL logging:
# In settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

Manual query inspection:

from django.db import connection
from main_app.models import Cat

# See what queries are executed
cats = Cat.objects.filter(user__username='test')
print(connection.queries[-1]['sql'])  # Last query executed

EXPLAIN ANALYZE SELECT * FROM main_app_cat WHERE user_id = 1;

3. Data Debugging
Django shell for data inspection:

python manage.py shell
from main_app.models import Cat, User

# Check data
users = User.objects.all()
for user in users:
    print(f"User: {user.username}")
    cats = Cat.objects.filter(user=user)
    print(f"  Cats: {cats.count()}")

# Check relationships
cat = Cat.objects.first()
if cat:
    print(f"Cat: {cat.name}")
    print(f"Feedings: {cat.feedings.count()}")
    print(f"Toys: {cat.toys.count()}")


. Migration Debugging
Check migration files:
ls main_app/migrations/
# Look for numbered migration files
Reverse migrations (for testing):
python manage.py migrate main_app 0001  # Go back to first migration
python manage.py migrate main_app zero  # Remove all migrations
Debug migration issues:
# Check if migrations are applied
from django.core.management import execute_from_command_line
execute_from_command_line(['manage.py', 'showmigrations', 'main_app'])


Popular PostgreSQL Debugging Methods
brew install pgadmin4
# Or download from pgadmin.org

Common commands:

# Connect to database
psql -d catcollector -U catcollector_user

# List tables
\dt

# Describe table
\d main_app_cat

# View data
SELECT * FROM main_app_cat LIMIT 5;

# Check indexes
\di

# Show running queries
SELECT * FROM pg_stat_activity;

# Exit
\q

3. Django Debug Toolbar (Database Tab)
Django Debug Toolbar (Database Tab)
Shows:

Number of queries executed
Query execution time
Duplicate queries
Query parameters


4. PostgreSQL Logs
Enable logging in postgresql.conf:log_statement = 'all'
log_directory = 'pg_log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'



View logs:

tail -f /usr/local/var/log/postgres.log  # macOS with Homebrew
tail -f /var/log/postgresql/postgresql-13-main.log  # Ubuntu

Step-by-Step Debugging Workflow

Step 1: Verify Setup
# Check PostgreSQL service
brew services list | grep postgresql

# Test connection
psql -d catcollector -U catcollector_user -c "SELECT version();"

# Check Django connection
python manage.py dbshell -c "SELECT 1;"

Step 2: Check Migrations

python manage.py showmigrations main_app
python manage.py migrate --dry-run  # See what would be applied


Step 3: Test Models


python manage.py shell


from main_app.models import Cat, Feeding
# Test model creation
cat = Cat(name="Test", breed="Tabby", age=2, user_id=1)
cat.save()
print(f"Created cat: {cat.id}")

# Test relationships
feeding = Feeding(date="2024-01-01", meal="B", cat=cat)
feeding.save()
print(f"Cat has {cat.feedings.count()} feedings")

Step 4: Test Views & URLs
from django.test import Client
from django.contrib.auth.models import User

client = Client()
user = User.objects.create_user('test', 'test@test.com', 'pass')
client.login(username='test', password='pass')

# Test URL resolution
from django.urls import reverse
url = reverse('cat-index')
response = client.get(url)
print(f"Status: {response.status_code}")


Step 5: Monitor Queries
# Enable query logging
import logging
logging.basicConfig()
logging.getLogger('django.db.backends').setLevel(logging.DEBUG)

# Run a view that queries the database
response = client.get('/cats/')

Common Issues & Solutions
1. Connection Issues
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Check user permissions
psql postgres -c "SELECT * FROM pg_roles WHERE rolname='catcollector_user';"

2. Migration Conflicts
# Fake migrations if needed
python manage.py migrate --fake main_app 0001

# Reset migrations
python manage.py migrate main_app zero
rm main_app/migrations/0*.py
python manage.py makemigrations
python manage.py migrate


3. Data Integrity Issues
-- Check for orphaned records
SELECT * FROM main_app_feeding WHERE cat_id NOT IN (SELECT id FROM main_app_cat);

-- Fix foreign key issues
DELETE FROM main_app_feeding WHERE cat_id NOT IN (SELECT id FROM main_app_cat);

4. Performance Issues
-- Check slow queries
SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;

-- Analyze table
ANALYZE main_app_cat;

-- Check indexes
SELECT * FROM pg_indexes WHERE tablename = 'main_app_cat';

