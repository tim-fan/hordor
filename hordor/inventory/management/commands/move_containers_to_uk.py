from django.core.management.base import BaseCommand, CommandError
from inventory.models import Container, Item

"""
DANGER!


This sets all objects to UK container

Used to help when moving to US.

Probably don't want to do this ever again.

Have commented `.save` to prevent updating again accidentally.

Keeping this script as an example management command
"""





class Command(BaseCommand):


    def handle(self, *args, **options):
        print("hi")
        # # print(Item.objects.all())
        # for item in Item.objects.all():
        #     print(item)
        #     print(item.container)
        uk = Container.objects.get(name="UK")
        # move all containers to UK
        for container in Container.objects.all():
            # print(container.container)
            if container.container == uk:
                # item.container = uk_container
                container.delete()
                print(f"delete {container}")
                # container.save()
                
