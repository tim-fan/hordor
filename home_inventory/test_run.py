import django
django.setup()
# from inventory.models import Toy, Box
from inventory.models import Item, Container

print("run")
c1 = Container.objects.first()
c2 = Container.objects.last()
i1 = Item.objects.first()

print("{} containers".format(Container.objects.count()))
print("{} items".format(Item.objects.count()))
print("{} items in container1".format(c1.stored_items.count()))
print("{} containers in container1".format(c1.stored_containers.count()))
print("Item1 container: {}".format(i1.container))
print("Container2 container: {}".format(c2.container))
print("Container1 container: {}".format(c1.container))

