from typing import Any, Dict, Optional, Type
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models.query import QuerySet
from django.db.models import Q
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, reverse
from django.utils.translation import gettext_lazy as _
from . models import Car, OrderEntry, Service, Order
from django.views import generic
from . forms import OrderReviewForm, OrderForm
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def profile_view(request):
    # Your view logic here
    return render(request, 'profile.html')


def index(request):
    cars = Car.objects.all().count()
    all_services = Service.objects.all()
    clean_service_names = [service.name for service in all_services]
    services = Service.objects.all().count()
    new_services = OrderEntry.objects.filter(status__exact="new").count()
    processing_services = OrderEntry.objects.filter(status__exact="processing").count()
    completed_services = OrderEntry.objects.filter(status__exact="complete").count()
    canceled_services = OrderEntry.objects.filter(status__exact="cancelled").count()

    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1

    context = {
        'cars': cars,
        'services': services,
        'new_services': new_services,
        'processing_services': processing_services,
        'completed_services': completed_services,
        'canceled_services': canceled_services,
        'all_services': clean_service_names,
        'num_visits': num_visits,
    }
    return render(request, 'service/index.html', context)


def car_list(request):
    qs = Car.objects
    query = request.GET.get('query')
    if query:
        qs = qs.filter(
            Q(model__year__istartswith=query) |
            Q(model__model__istartswith=query) |
            Q(model__make__istartswith=query)
            # Q(vin_code__icontains=query)
        )
    else:
        qs = qs.all()
    paginator = Paginator(qs, 2)
    page_number = request.GET.get('page')
    paged_cars = paginator.get_page(page_number)
    context = {
        'cars': paged_cars
    }
    return render(request, 'service/car_list.html', context=context)


def car_detail(request, pk: int):
    car = get_object_or_404(Car, pk=pk)
    return render(request, 'service/car_detail.html', {'car': car})


class OrderListView(generic.ListView):
    model = Order
    paginate_by = 4
    context_object_name = 'orders'
    template_name = 'service/order_list.html'

    def get_queryset(self) -> QuerySet[Any]:
        qs = super().get_queryset()
        query = self.request.GET.get('query')
        if query:
            qs = qs.filter(
                Q(order_entries__price__icontains=query) |
                Q(car__customer__istartswith=query) |
                Q(car__licence_plate__istartswith=query) |
                Q(car__vin_code__istartswith=query) |
                Q(car__model__make__icontains=query)
            )
        return qs


class OrderDetailView(generic.edit.FormMixin, generic.DetailView):
    model = Order
    template_name = 'service/order_detail.html'
    form_class = OrderReviewForm

    def get_initial(self) -> Dict[str, Any]:
        initial = super().get_initial()
        initial['order'] = self.get_object()
        initial['reviewer'] = self.request.user
        return initial

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form: Any) -> HttpResponse:
        form.instance.order = self.get_object()
        form.instance.reviewer = self.request.user
        form.save()
        messages.success(self.request, _('Review posted!'))
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse('order_detail', kwargs={'pk': self.get_object().pk})


class UserOrdersListView(LoginRequiredMixin, generic.ListView):
    model = Order
    template_name = 'service/user_orders.html'
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Any]:
        qs = super().get_queryset()
        qs = qs.filter(car__client=self.request.user).order_by('due_back')
        return qs


class UserCarListView(LoginRequiredMixin, generic.ListView):
    model = Car
    template_name = 'service/user_car_list.html'
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Any]:
        qs = super().get_queryset()
        qs = qs.filter(client=self.request.user)
        return qs


class UserOrderDetailView(LoginRequiredMixin, generic.DetailView):
    model = Order
    template_name = 'user_order.html'


class UserOrderCreateView(LoginRequiredMixin, generic.CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'service/user_order_form.html'

    def get_form(self, form_class: Type[BaseModelForm] | None = form_class) -> BaseModelForm:
        form = super().get_form(form_class)
        if not form.is_bound:
            form.fields["car"].queryset = Car.objects.filter(client=self.request.user)
        return form

    def get_success_url(self) -> str:
        return reverse('my-order-new')

    def form_valid(self, form):
        form.instance.order = self.request.user
        return super().form_valid(form)

    def get_absolute_url(self):
        return reverse('order_detail', args=[str(self.id)])

# Create your views here.
