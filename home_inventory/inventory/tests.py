from django.test import TestCase

# Create your tests here.

from .models import Item, Container

class ItemAndContainerModelTests(TestCase):

    def test_add_contents(self):
        """
        """
        i1 = Item(name="i1")
        i1.save()
        c1 = Container(name="c1")
        c1.save()
        c2 = Container(name="c2")
        c2.save()
        c1.stored_items.add(i1)
        c1.stored_containers.add(c2)

        self.assertEqual(Item.objects.count(), 1)
        self.assertEqual(Container.objects.count(), 2)
        self.assertEqual(c1.stored_items.count(), 1)
        self.assertEqual(c1.stored_containers.count(), 1)
        self.assertIs(c2.container, c1)