import django
django.setup()


from inventory.models import Item, Container

print("setup")

i = Item(name="i1")
i.save()
c1 = Container(name="c1")
c1.save()
c2 = Container(name="c2")
c2.save()

print(dir(c1))
c1.stored_items.add(i)
c1.stored_containers.add(c2)
print("{} containers".format(Container.objects.count()))
print("{} items".format(Item.objects.count()))
print("{} items in container1".format(Container.objects.first().stored_items.count()))
print("{} containers in container1".format(Container.objects.first().stored_containers.count()))
