from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    def alive(self):
        return self.filter(deleted_at__isnull=True)

    def dead(self):
        return self.exclude(deleted_at__isnull=True)


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        # по умолчанию возвращаем только "не удалённые"
        return SoftDeleteQuerySet(self.model, using=self._db).alive()


class BaseSoftDeleteModel(models.Model):
    """
    Базовая модель с soft-delete:
    delete() = проставить deleted_at
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()                 # только живые
    all_objects = SoftDeleteQuerySet.as_manager()  # все, включая удалённые

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def hard_delete(self):
        super().delete()


class Course(BaseSoftDeleteModel):
    """
    Course:
    - title
    - description (optional)
    - is_active (default True)
    - owner (FK to user, related_name='owned_courses')
    - created_at, updated_at, deleted_at (из BaseSoftDeleteModel)
    """
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="owned_courses",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.title


class Lesson(BaseSoftDeleteModel):
    """
    Lesson:
    - course (FK, related_name='lessons')
    - title
    - content
    - order (DecimalField, порядок; "по умолчанию наверху" зададим в логике создания)
    - indentation (1..5)
    - is_published (default False)
    """
    course = models.ForeignKey(
        Course,
        related_name="lessons",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    order = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_index=True,
    )
    indentation = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
    )
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.course_id} - {self.title}"

    @staticmethod
    def get_top_order_for_course(course):
        """
        Вернуть значение order так, чтобы урок был "на самом верху".
        """
        first = Lesson.objects.filter(course=course).order_by("order").first()
        if first is None:
            return Decimal("1000.00")  # первый урок в курсе
        return first.order - Decimal("10.00")

    @staticmethod
    def get_last_order_for_course(course):
        """
        Вернуть значение order так, чтобы урок был "в самом конце".
        """
        last = Lesson.objects.filter(course=course).order_by("-order").first()
        if last is None:
            return Decimal("1000.00")
        return last.order + Decimal("10.00")

