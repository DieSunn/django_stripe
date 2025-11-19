from django.db import models

class Item(models.Model):
    """
    Модель товара (Item).
    Хранит информацию о названии, описании и цене отдельного продукта.
    """
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    price = models.IntegerField(help_text="Цена в минимальных единицах валюты (центы)", verbose_name="Цена")
    currency = models.CharField(max_length=3, default='usd', verbose_name="Валюта")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

class Discount(models.Model):
    """
    Модель скидки (Discount).
    Используется для создания купонов в Stripe.
    """
    name = models.CharField(max_length=50, verbose_name="Название скидки")
    percent_off = models.IntegerField(help_text="Процент скидки (1-100)", verbose_name="Процент")
    
    def __str__(self):
        return f"{self.name} (-{self.percent_off}%)"

    class Meta:
        verbose_name = "Скидка"
        verbose_name_plural = "Скидки"

class Tax(models.Model):
    """
    Модель налога (Tax).
    Используется для добавления налоговой ставки в Stripe.
    """
    name = models.CharField(max_length=50, verbose_name="Название налога")
    rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Ставка налога (например, 20.00)", verbose_name="Ставка")
    
    def __str__(self):
        return f"{self.name} ({self.rate}%)"

    class Meta:
        verbose_name = "Налог"
        verbose_name_plural = "Налоги"

class Order(models.Model):
    """
    Модель заказа (Order).
    Объединяет несколько товаров, а также может иметь примененную скидку и налог.
    """
    items = models.ManyToManyField(Item, verbose_name="Товары")
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Скидка")
    tax = models.ForeignKey(Tax, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Налог")
    
    def __str__(self):
        return f"Заказ #{self.pk}"
    
    def get_total_price(self):
        """
        Рассчитывает итоговую стоимость заказа с учетом скидок и налогов.
        Используется только для отображения в шаблоне (Stripe считает сам).
        """
        total = sum([item.price for item in self.items.all()])
        if self.discount:
            total = total * (1 - self.discount.percent_off / 100)
        if self.tax:
            total = total * (1 + float(self.tax.rate) / 100)
        return int(total)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"