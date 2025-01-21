# Open Camp's School Platform

[open camp][oc]'s learning platform.

## Development

This project uses Django, TailwindCSS, and htmx. We use Django templates without
using an external frontend framework like React or Vue, while TailwindCSS is used for
styling, and htmx for dynamic content.


## Project Structure

We use the standard project layout for Django projects, with a few differences:
- All templates are stored in the `templates` directory, and not in their individual apps

Notable apps in this project are:

- `db` app holds the `BaseModel` and `CreatedUpdatedMixin` for use by models in other apps
- `landing` app is the equivalent to Linktree for teachers
- `classes` app allows teachers to sell classes (1-1, group, etc.)
- `users` app holds the user model and authentication views
- `integration` app handles external integrations like Google login and Google Calendar to be used by other apps

### Setting Up For Development

**Setting Up Django**

1. Install requirements using `pip install -r requirements.txt` (We recommend using `uv` if you have it installed)
2. Copy the sample `.env.exmaple` file to `.env` - there is no need to add or change any values inside
3. Run the tests using `pytest . -n auto` and ensure that they pass

Run the project using Django's built-in development server with the following command:

```
python manage.py runserver
```

**Setting Up TailwindCSS**

We do not need to use the `npm install` version of TailwindCSS. Instead,
download the latest stable binary for TailwindCSS from their [releases page][2], and
ensure that it is available on your `$PATH`.

Run the following command in one of your terminal tabs / windows and leave it
running to watch for changes in your Django templates:

```
tailwindcss -i static/css/input.css -o static/css/app.css -m -w
```

Note: `-m` is for minification, and `-w` is for watching for changes so you
do not need to manually re-run Tailwind each time you change the templates.

**Code Formatting**

We use `ruff` for formatting, so please ensure that it is [properly integrated][1] with your editor of choice.

**Git Working Style**

- Create a new branch off `main` for every change you plan to make
- Make as many commits and changes as you need to. Push your changes often
- Ensure that CI passes with no errors
- Create a pull request for review once it is ready, and tag the reviewer
- Once the pull request is reviewed, **ensure that you choose the "Squash and Merge" option** to merge the branch into `main`

We do not have a fixed branch naming style. Use your best judgement when naming branches.


# License

Copyright 2025 Victor Neo

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


[1]: https://docs.astral.sh/ruff/editors/setup/
[2]: https://github.com/tailwindlabs/tailwindcss/releases
[oc]: https://opencamp.cc