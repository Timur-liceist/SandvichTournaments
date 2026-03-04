from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from news.forms import NewsForm
from news.models import GeneralNewsModel


class AllGeneralNewsView(View):
    def get(self, request):
        general_news = GeneralNewsModel.objects.select_related("author").all()
        context = {
            "general_news": general_news,
        }
        return render(
            request,
            "news/general_news.html",
            context=context,
        )


class CreateGeneralNewsView(LoginRequiredMixin, View):

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("users:not_logined")

        if not request.user.is_superuser:
            return redirect("forbidden")

        form = NewsForm()

        context = {
            "form": form,
        }

        return render(
            request,
            "news/create_news.html",
            context=context,
        )

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect("users:not_logined")

        if not request.user.is_superuser:
            return redirect("forbidden")

        form = NewsForm(request.POST)

        if form.is_valid():
            news = form.save()
            news.author = request.user
            news.save()

        return redirect("news:general_news")
class EditGeneralNewsView(LoginRequiredMixin, View):

    def get(self, request, news_id):
        if not request.user.is_authenticated:
            return redirect("users:not_logined")

        if not request.user.is_superuser:
            return redirect("forbidden")

        news_for_update = get_object_or_404(GeneralNewsModel, id=news_id)

        form = NewsForm(instance=news_for_update)

        context = {
            "form": form,
        }

        return render(
            request,
            "news/edit_news.html",
            context=context,
        )

    def post(self, request, news_id):
        if not request.user.is_authenticated:
            return redirect("users:not_logined")

        if not request.user.is_superuser:
            return redirect("forbidden")

        news_for_update = get_object_or_404(GeneralNewsModel, id=news_id)

        form = NewsForm(request.POST, instance=news_for_update)

        if form.is_valid():
            form.save()

        return redirect("news:general_news")
