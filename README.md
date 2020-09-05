# Home Inventory

Django app for managing home inventory.

<img src="doc/screenshot_containers.png" alt="docker icon" width="800"/>

## Run

```bash
python manage.py runserver
```

## Development
`.devcontainer` handles setup for development.

(Use with vscode Remote-Containers extension)

## ToDo

* Item storage history (dates of container change) 
  * Try https://django-simple-history.readthedocs.io/en/latest/index.html
* Table view with search
* Object delete views
  * see https://docs.djangoproject.com/en/3.1/ref/class-based-views/generic-editing/#django.views.generic.edit.DeleteView
  * see http://www.learningaboutelectronics.com/Articles/How-to-create-a-delete-view-with-Python-in-Django.php
* Compress images on save
  * try https://stackoverflow.com/questions/33077804/losslessly-compressing-images-on-django
  * better to keep separate thumbnails and full-res images?
    * refer https://code.djangoproject.com/wiki/ThumbNails
  * Note, until this is implemented, can periodically run this to keep files small:
  `jpegoptim --size=100k media/images/*`
      * note size=100k give some pretty significant color distortion
* Handle case when item has no photo associated in detail views
* Bulk-add objects to a container
* Add fields
    * Item value
    * Description
* Add container forest view
    * something like https://codepen.io/dsheiko/pen/MvEpXm/
* Item tags / categorisation
* Handle multiple photos per object
* Container detail view, items list - have a card with a '+', for 'add another'. Similar for adding containers
* Fix item list in container card running over card boundary
* Host a live example site somewhere/somehow

