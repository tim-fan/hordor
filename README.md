# Home Inventory

Django app for managing home inventory.

## Run

```bash
python manage.py runserver
```

## Development
`.devcontainer` handles setup for development.

(Use with vscode Remote-Containers extension)

## ToDo

* View containers as bootstap well,  or similar, showing contents inside the well
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
* Item storage history (dates of container change) 
  * Try https://django-simple-history.readthedocs.io/en/latest/index.html
* Bulk-add objects to a container
* Add fields
    * Item value
    * Description
* Add container forest view
    * something like https://codepen.io/dsheiko/pen/MvEpXm/
* Item tags / categorisation
* Handle multiple photos per object

