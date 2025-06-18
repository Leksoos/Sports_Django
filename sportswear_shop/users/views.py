from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse

def register(request: HttpRequest) -> HttpResponse:
    """
    Обрабатывает регистрацию нового пользователя.
    
    При GET-запросе отображает форму регистрации.
    При POST-запросе валидирует и сохраняет пользователя,
    затем перенаправляет на страницу входа.
    
    :param request: объект HTTP-запроса
    :return: HTTP-ответ с рендером страницы или редирект
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})
