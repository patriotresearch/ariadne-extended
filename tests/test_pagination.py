from ariadne_extended.cursor_pagination import InternalPaginator, InvalidCursor
# from charges.models import Charge
from django.test import TestCase
from model_bakery import baker

from .models import Charge


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
        cls.charges = []
        for i in range(20):
            charge = baker.make(
                Charge,
                item__number="%s" % (i + 20),
                item__description="description %s" % i,
                order=i,
            )
            cls.charges.append(charge)
        cls.paginator = InternalPaginator(Charge.objects.all(), ("order",))

    def test_first_page(self):
        page = self.paginator.page(first=2)
        self.assertSequenceEqual(page, [self.charges[0], self.charges[1]])
        self.assertTrue(page.has_next)
        self.assertFalse(page.has_previous)

    def test_second_page(self):
        previous_page = self.paginator.page(first=2)
        cursor = self.paginator.cursor(previous_page[-1])
        page = self.paginator.page(first=2, after=cursor)
        self.assertSequenceEqual(page, [self.charges[2], self.charges[3]])
        self.assertTrue(page.has_next)
        self.assertTrue(page.has_previous)

    def test_last_page(self):
        previous_page = self.paginator.page(first=18)
        cursor = self.paginator.cursor(previous_page[-1])
        page = self.paginator.page(first=2, after=cursor)
        self.assertSequenceEqual(page, [self.charges[18], self.charges[19]])
        self.assertFalse(page.has_next)
        self.assertTrue(page.has_previous)

    def test_incomplete_last_page(self):
        previous_page = self.paginator.page(first=18)
        cursor = self.paginator.cursor(previous_page[-1])
        page = self.paginator.page(first=100, after=cursor)
        self.assertSequenceEqual(page, [self.charges[18], self.charges[19]])
        self.assertFalse(page.has_next)
        self.assertTrue(page.has_previous)


class TestBackwardsPagination(TestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.charges = []
        for i in range(20):
            post = baker.make(
                Charge,
                item__number="%s" % (i + 20),
                item__description="description %s" % i,
                order=i,
            )
            cls.charges.append(post)
        cls.paginator = InternalPaginator(Charge.objects.all(), ("order",))

    def test_first_page(self):
        page = self.paginator.page(last=2)
        self.assertSequenceEqual(page, [self.charges[18], self.charges[19]])
        self.assertTrue(page.has_previous)
        self.assertFalse(page.has_next)

    def test_second_page(self):
        previous_page = self.paginator.page(last=2)
        cursor = self.paginator.cursor(previous_page[0])
        page = self.paginator.page(last=2, before=cursor)
        self.assertSequenceEqual(page, [self.charges[16], self.charges[17]])
        self.assertTrue(page.has_previous)
        self.assertTrue(page.has_next)

    def test_last_page(self):
        previous_page = self.paginator.page(last=18)
        cursor = self.paginator.cursor(previous_page[0])
        page = self.paginator.page(last=2, before=cursor)
        self.assertSequenceEqual(page, [self.charges[0], self.charges[1]])
        self.assertFalse(page.has_previous)
        self.assertTrue(page.has_next)

    def test_incomplete_last_page(self):
        previous_page = self.paginator.page(last=18)
        cursor = self.paginator.cursor(previous_page[0])
        page = self.paginator.page(last=100, before=cursor)
        self.assertSequenceEqual(page, [self.charges[0], self.charges[1]])
        self.assertFalse(page.has_previous)
        self.assertTrue(page.has_next)


class TestTwoFieldPagination(TestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.charges = []
        data = [(0, "B"), (0, "C"), (0, "D"), (1, "A")]
        for order, description in data:
            charge = baker.make(
                Charge,
                item__number="%s" % (order + 20),
                item__description=description,
                order=order,
            )
            cls.charges.append(charge)

    def test_order(self):
        paginator = InternalPaginator(
            Charge.objects.all(), ("order", "item__description")
        )
        previous_page = paginator.page(first=2)
        self.assertSequenceEqual(previous_page, [self.charges[0], self.charges[1]])
        cursor = paginator.cursor(previous_page[-1])
        page = paginator.page(first=2, after=cursor)
        self.assertSequenceEqual(page, [self.charges[2], self.charges[3]])

    def test_reverse_order(self):
        paginator = InternalPaginator(
            Charge.objects.all(), ("-order", "-item__description")
        )
        previous_page = paginator.page(first=2)
        self.assertSequenceEqual(previous_page, [self.charges[3], self.charges[2]])
        cursor = paginator.cursor(previous_page[-1])
        page = paginator.page(first=2, after=cursor)
        self.assertSequenceEqual(page, [self.charges[1], self.charges[0]])

    def test_mixed_order(self):
        with self.assertRaises(InvalidCursor):
            InternalPaginator(Charge.objects.all(), ("order", "-item__description"))


class TestRelationships(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.charges = []
        for i in range(20):
            post = baker.make(
                Charge, item__id=(1 if i % 2 else 2), item__number="%s" % "A item" if i % 2 else "B item", order=i
            )
            cls.charges.append(post)
        cls.paginator = InternalPaginator(
            Charge.objects.all(), ("item__number", "order")
        )

    def test_first_page(self):
        page = self.paginator.page(first=2)
        self.assertSequenceEqual(page, [self.charges[1], self.charges[3]])

    def test_after_page(self):
        cursor = self.paginator.cursor(self.charges[17])
        page = self.paginator.page(first=2, after=cursor)
        self.assertSequenceEqual(page, [self.charges[19], self.charges[0]])
