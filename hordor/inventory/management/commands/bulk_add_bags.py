from django.core.management.base import BaseCommand, CommandError
from inventory.models import Container
from datetime import datetime, timedelta


class Command(BaseCommand):


    def handle(self, *args, **options):
        print("hi")

        bag_names = [f"Bag {i}" for i in range(60)]
        # # print(Item.objects.all())
        # for item in Item.objects.all():
        #     print(item)
        #     print(item.container)
        us_container = Container.objects.get(name="US")
        # move all containers to UK
        for i, bag_name in enumerate(bag_names):
            # print(container.container)
            try:
                bag = Container.objects.get(name=bag_name)

            except Container.DoesNotExist:
                print(f"{bag_name} does not exist")
                bag = Container.objects.create(
                    name=bag_name
                )
                bag.container = us_container
            # overwrite creation date to get the ordering I want
            bag.creation_date = datetime(2000, 1, 1) + timedelta(days=i)
            bag.save()

        # all containers in US
        # for container in Container.objects.all():
        #     if container.name.startswith("Bag"):
        #         if not container.container:
        #             print(f"{container.name}: {container.container}")
        #             container.container = us_container
        #             container.save()
                
