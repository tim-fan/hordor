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

* Add photo upload for containers
* Show photos on object views (detail and list)
* Support image upload via android camera
* Bulk-add objects to a container
* Add fields
    * Item value
    * Description
* Add container forest view
* Item tags / categorisation
* Handle multiple photos per object
* Item storage history (dates of container change) 
* Validation - no cyclical container relations (A contains B, B contains A)