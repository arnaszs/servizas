from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from datetime import date


User = get_user_model()


class Car(models.Model):
    client = models.ForeignKey(
        User,
        verbose_name=_("client"),
        related_name="cars",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        )
    license_plate = models.CharField(
        _("License Plate"),
        max_length=17,
        )
    vin_code = models.CharField(
        _("VIN Code"),
        max_length=50,
        )

    class Meta:
        ordering = ["license_plate"]
        verbose_name = _("car")
        verbose_name_plural = _("cars")

    def __str__(self):
        return self.license_plate

    def get_absolute_url(self):
        return reverse("car_detail", kwargs={"pk": self.pk})


class CarModel(models.Model):
    make = models.CharField(
        _("Make"),
        max_length=99,
        )
    model = models.CharField(
        _("Model"),
        max_length=99,
        )
    year = models.PositiveIntegerField(_("Year"))
    engine = models.CharField(
        _("Engine"),
        max_length=99,
        )

    class Meta:
        ordering = ["year"]
        verbose_name = _("car model")
        verbose_name_plural = _("car models")

    def __str__(self):
        return f"{self.make} {self.model} {self.year} {self.engine}"

    def get_absolute_url(self):
        return reverse("carmodel_detail", kwargs={"pk": self.pk})


class Service(models.Model):
    name = models.CharField(
        _("Name"),
        max_length=99,
        )
    price = models.DecimalField(
        _("Price"),
        max_digits=19,
        decimal_places=2,
        db_index=True,
        null=True
        )

    class Meta:
        ordering = ["name", "id"]
        verbose_name = _("service")
        verbose_name_plural = _("services")

    def __str__(self):
        return self.name


class Order(models.Model):
    date = models.DateField(
        _("date"),
        auto_now=False,
        auto_now_add=False,
        null=True,
        blank=True,
        )
    price = models.DecimalField(
        _("Price"),
        max_digits=19,
        decimal_places=2,
        default=0,
        db_index=True,
        null=True,
        )
    car = models.ForeignKey(
        Car,
        verbose_name=_("car"),
        related_name='orders',
        on_delete=models.CASCADE,
        null=True,
        )

    due_back = models.DateField(
        _("due back"),
        blank=True,
        null=True,
        db_index=True,
        )

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

    class Meta:
        ordering = ["date", "id"]
        verbose_name = _("order")
        verbose_name_plural = _("orders")

    def __str__(self):
        return f"Order #{self.pk} | {self.car} | {self.date}"

    def get_absolute_url(self):
        return reverse("order_detail", kwargs={"pk": self.pk})

    @property
    def client(self):
        return self.car.client


class OrderEntry(models.Model):
    quantity = models.IntegerField(
        _("Quantity"),
        default=1
        )
    price = models.DecimalField(
        _("Price"),
        max_digits=19,
        decimal_places=2,
        null=True,
        db_index=True,
        default=0
        )
    total = models.DecimalField(
        _("Total"),
        max_digits=19,
        decimal_places=2,
        default=0
        )
    service = models.ForeignKey(
        Service,
        verbose_name=_("service"),
        related_name="order_entries",
        on_delete=models.CASCADE,
        null=True)
    order = models.ForeignKey(
        Order,
        verbose_name=_("order"),
        related_name="order_entries",
        on_delete=models.CASCADE,
        null=True)

    STATUS_CHOICES = [
        ("new", "New"),
        ("processing", "Processing"),
        ("complete", "Complete"),
        ("cancelled", "Cancelled"),
    ]

    status = models.CharField(
        _("Status"),
        max_length=19,
        choices=STATUS_CHOICES,
        default="new",
        db_index=True)

    class Meta:
        verbose_name = _("order entry")
        verbose_name_plural = _("order entries")

    def __str__(self):
        return f"{self.service} {self.price} {self.quantity}"

    def get_absolute_url(self):
        return reverse("orderentry_detail", kwargs={"pk": self.pk})

    def get_color(self):
        colors = {
            "new": "blue",
            "processing": "orange",
            "complete": "green",
            "cancelled": "red",
        }
        default_color = "black"
        return colors.get(self.status, default_color)

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status)

    def save(self, *args, **kwargs):
        if self.price == 0:
            self.price = self.service.price
        if self.status != "cancelled":
            self.total = self.price * self.quantity
        super().save(*args, **kwargs)
        self.order.price = self.order.order_entries.exclude(status="cancelled").aggregate(models.Sum("total"))["total__sum"]
        self.order.save()


class OrderReview(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name=_("order"),
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    reviewer = models.ForeignKey(
        User,
        verbose_name=_("reviewer"),
        on_delete=models.SET_NULL,
        related_name='order_reviews',
        null=True, blank=True,
    )
    reviewed_at = models.DateTimeField(
        _("Reviewed"),
        auto_now_add=True
        )
    content = models.TextField(
        _("content"),
        max_length=4000
        )

    class Meta:
        ordering = ['-reviewed_at']
        verbose_name = _("order review")
        verbose_name_plural = _("order reviews")

    def __str__(self):
        return f"{self.reviewed_at}: {self.reviewer}"

    def get_absolute_url(self):
        return reverse("orderreview_detail", kwargs={"pk": self.pk})
