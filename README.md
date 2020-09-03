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

* Object delete views
  * see https://docs.djangoproject.com/en/3.1/ref/class-based-views/generic-editing/#django.views.generic.edit.DeleteView
  * see http://www.learningaboutelectronics.com/Articles/How-to-create-a-delete-view-with-Python-in-Django.php
* Compress images on save
  * try https://stackoverflow.com/questions/33077804/losslessly-compressing-images-on-django
* Bootstrap styling on forms?
* Handle case when item has no photo associated
* Item storage history (dates of container change) 
  * Try https://django-simple-history.readthedocs.io/en/latest/index.html
* Bulk-add objects to a container
* Add fields
    * Item value
    * Description
* Add container forest view
    * something like https://codepen.io/dsheiko/pen/MvEpXm/
* gallery view
* Item tags / categorisation
* Handle multiple photos per object

