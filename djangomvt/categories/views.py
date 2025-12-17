from django.shortcuts import redirect, render
from .models import Category, ImagesCategory
from django.http import JsonResponse
import uuid
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.text import slugify
from urllib.parse import urlparse
from urllib.request import urlopen, Request
import re
from django.core.files.base import ContentFile

# Create your views here.

def show_categories(request):
    categories = Category.objects.all()
    return render(request, "categories.html", {'categories': categories})


def _unique_slug(base_slug: str) -> str:
    slug = base_slug
    i = 1
    while Category.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{i}"
        i += 1
    return slug


def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')

        if name and description:
            category = Category(
                name=name,
                slug=_unique_slug(slugify(name)),
                description=description
            )
            category.save()

            media_prefix = (settings.MEDIA_URL or '/media/') + 'images/'
            # захист від подвійних слешів
            media_prefix = media_prefix.replace('//', '/')
            image_srcs = re.findall(r"<img[^>]+src=['\"]([^'\"]+)['\"]", description or '', flags=re.IGNORECASE)
            for src in image_srcs:
                if media_prefix in src:
                    # отримати відносний шлях від кореня медіа
                    try:
                        rel_path = src.split(settings.MEDIA_URL, 1)[1]
                    except Exception:
                        # якщо MEDIA_URL не знайдено, спробуємо за префіксом
                        rel_path = src.split(media_prefix.split('images/')[0], 1)[-1]
                    # Переконаємось що шлях починається з 'images/'
                    if not rel_path.startswith('images/'):
                        # видалити можливий початковий слеш
                        rel_path = rel_path.lstrip('/')
                        if not rel_path.startswith('images/'):
                            continue
                    # Створюємо запис з існуючим файлом у сховищі
                    ImagesCategory.objects.create(idcategory=category, image=rel_path)

            return redirect('categories:show_categories')
        else:
            return render(request, 'add_category.html', {'error': 'Заповніть всі обов\'язкові поля'})
    return render(request, 'add_category.html')


def _unique_filename(original_name: str) -> str:
    base, ext = os.path.splitext(original_name)
    if not ext:
        ext = '.jpg'
    return f"{uuid.uuid4().hex}{ext.lower()}"


def upload_image(request):
    """Приймає картинку як файл або як URL, зберігає в MEDIA_ROOT/images
    та повертає JSON з публічним URL та відносним шляхом для БД.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'images'),
                           base_url=(settings.MEDIA_URL or '/media/') + 'images/')

    # файл у request.FILES['file']
    upload = request.FILES.get('file')
    if upload:
        filename = _unique_filename(upload.name)
        saved_name = fs.save(filename, upload)
        url = fs.url(saved_name)
        return JsonResponse({'url': url, 'path': f'images/{saved_name}'})

    # URL у формі (не JSON для простоти)
    src_url = request.POST.get('url') or request.GET.get('url')
    if src_url:
        try:
            parsed = urlparse(src_url)
            # Витягнемо розширення з URL якщо є
            ext = os.path.splitext(parsed.path)[1] or '.jpg'
            filename = _unique_filename('from_url' + ext)
            # Завантаження з URL (заголовок User-Agent щоб деякі сайти давали файл)
            req = Request(src_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urlopen(req, timeout=10) as resp:
                data = resp.read()
            saved_name = fs.save(filename, ContentFile(data))
            url = fs.url(saved_name)
            return JsonResponse({'url': url, 'path': f'images/{saved_name}'})
        except Exception as e:
            return JsonResponse({'error': f'Failed to fetch image: {e}'}, status=400)

    return JsonResponse({'error': 'No file or url provided'}, status=400)