from django.db import models
from ariadne_extended.cursor_pagination import InternalPaginator, InvalidCursor
# from charges.models import Charge
from django.test import TestCase
from model_bakery import baker


class Item(models.Model):
    number = models.TextField(max_length="25")
    description = models.TextField(max_length="25")


class Charge(models.Model):
    order = models.PositiveIntegerField()
    item = models.ForeignKey(Item, blank=True, null=True)


class TestNoArgs(TestCase):
    maxDiff = None

    def test_empty(self):
        paginator = InternalPaginator(Charge.objects.all(), ("id",))
        page = paginator.page()
        self.assertEqual(len(page), 0)
        self.assertFalse(page.has_next)
        self.assertFalse(page.has_previous)

    def test_with_items(self):
        for i in range(20):
            baker.make(Charge, item__description="description %s" % i)
        paginator = InternalPaginator(Charge.objects.all(), ("id",))
        page = paginator.page()
        self.assertEqual(len(page), 20)
        self.assertFalse(page.has_next)
        self.assertFalse(page.has_previous)


class TestForwardPagination(TestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.items = []
        for i in range(20):
            post = baker.make(
                Charge,
                item__number="%s" % (i + 20),
                item__description="description %s" % i,
                order=i,
            )
            cls.items.append(post)
        cls.paginator = InternalPaginator(Charge.objects.all(), ("order",))

    def test_first_page(self):
        page = self.paginator.page(first=2)
        self.assertSequenceEqual(page, [self.items[0], self.items[1]])
        self.assertTrue(page.has_next)
        self.assertFalse(page.has_previous)

    def test_second_page(self):
        previous_page = self.paginator.page(first=2)
        cursor = self.paginator.cursor(previous_page[-1])
        page = self.paginator.page(first=2, after=cursor)
        self.assertSequenceEqual(page, [self.items[2], self.items[3]])
        self.assertTrue(page.has_next)
        self.assertTrue(page.has_previous)

    def test_last_page(self):
        previous_page = self.paginator.page(first=18)
        cursor = self.paginator.cursor(previous_page[-1])
        page = self.paginator.page(first=2, after=cursor)
        self.assertSequenceEqual(page, [self.items[18], self.items[19]])
        self.assertFalse(page.has_next)
        self.assertTrue(page.has_previous)

    def test_incomplete_last_page(self):
        previous_page = self.paginator.page(first=18)
        cursor = self.paginator.cursor(previous_page[-1])
        page = self.paginator.page(first=100, after=cursor)
        self.assertSequenceEqual(page, [self.items[18], self.items[19]])
        self.assertFalse(page.has_next)
        self.assertTrue(page.has_previous)


class TestBackwardsPagination(TestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.items = []
        for i in range(20):
            post = baker.make(
                Charge,
                item__number="%s" % (i + 20),
                item__description="description %s" % i,
                order=i,
            )
            cls.items.append(post)
        cls.paginator = InternalPaginator(Charge.objects.all(), ("order",))

    def test_first_page(self):
        page = self.paginator.page(last=2)
        self.assertSequenceEqual(page, [self.items[18], self.items[19]])
        self.assertTrue(page.has_previous)
        self.assertFalse(page.has_next)

    def test_second_page(self):
        previous_page = self.paginator.page(last=2)
        cursor = self.paginator.cursor(previous_page[0])
        page = self.paginator.page(last=2, before=cursor)
        self.assertSequenceEqual(page, [self.items[16], self.items[17]])
        self.assertTrue(page.has_previous)
        self.assertTrue(page.has_next)

    def test_last_page(self):
        previous_page = self.paginator.page(last=18)
        cursor = self.paginator.cursor(previous_page[0])
        page = self.paginator.page(last=2, before=cursor)
        self.assertSequenceEqual(page, [self.items[0], self.items[1]])
        self.assertFalse(page.has_previous)
        self.assertTrue(page.has_next)

    def test_incomplete_last_page(self):
        previous_page = self.paginator.page(last=18)
        cursor = self.paginator.cursor(previous_page[0])
        page = self.paginator.page(last=100, before=cursor)
        self.assertSequenceEqual(page, [self.items[0], self.items[1]])
        self.assertFalse(page.has_previous)
        self.assertTrue(page.has_next)


class TestTwoFieldPagination(TestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.items = []
        data = [(0, "B"), (0, "C"), (0, "D"), (1, "A")]
        for order, description in data:
            post = baker.make(
                Charge,
                item__number="%s" % (order + 20),
                item__description=description,
                order=order,
            )
            cls.items.append(post)

    def test_order(self):
        paginator = InternalPaginator(
            Charge.objects.all(), ("order", "item__description")
        )
        previous_page = paginator.page(first=2)
        self.assertSequenceEqual(previous_page, [self.items[0], self.items[1]])
        cursor = paginator.cursor(previous_page[-1])
        page = paginator.page(first=2, after=cursor)
        self.assertSequenceEqual(page, [self.items[2], self.items[3]])

    def test_reverse_order(self):
        paginator = InternalPaginator(
            Charge.objects.all(), ("-order", "-item__description")
        )
        previous_page = paginator.page(first=2)
        self.assertSequenceEqual(previous_page, [self.items[3], self.items[2]])
        cursor = paginator.cursor(previous_page[-1])
        page = paginator.page(first=2, after=cursor)
        self.assertSequenceEqual(page, [self.items[1], self.items[0]])

    def test_mixed_order(self):
        with self.assertRaises(InvalidCursor):
            InternalPaginator(Charge.objects.all(), ("order", "-item__description"))


class TestRelationships(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.items = []
        for i in range(20):
            post = baker.make(
                Charge, item__number="%s" % "A item" if i % 2 else "B item", order=i
            )
            cls.items.append(post)
        cls.paginator = InternalPaginator(
            Charge.objects.all(), ("item__number", "order")
        )

    def test_first_page(self):
        page = self.paginator.page(first=2)
        self.assertSequenceEqual(page, [self.items[1], self.items[3]])

    def test_after_page(self):
        cursor = self.paginator.cursor(self.items[17])
        page = self.paginator.page(first=2, after=cursor)
        self.assertSequenceEqual(page, [self.items[19], self.items[0]])
