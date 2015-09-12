============================
Coding Style and Conventions
============================

When writing Python code for Misago, please familiarize yourself with and follow those documents:

1. `PEP 8 <http://www.python.org/dev/peps/pep-0008/>`_
2. `Django Coding Style and Conventions <https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/>`_

Those documents should give you solid knowledge of coding style and conventions that are followed by Python and Django programmers when writing code.

In addition to those guidelines, Misago defines set of additional convetions and good practices that will help you write better and easier code:


Models
======

Fields Order
------------

When declaring model's database fields, start with taxonomical foreign keys followed by fields that make this model identifiable to humans. Order of remaining fileds is completely up to you.

Thread model is great example of this convention. Thread is part of taxonomy (Forum), so first field defined is foreign key to Forum model. This is followed by two fields that humans will use to recognise this model: "title" that will be displayed in UI and "slug" that will be included in links to this thread. After those Thread model defines additional fields.

When declaring model database fields, make sure they are grouped together based on their purpose. Most common example is storage of user name and slug in addition to foreign key to User model. In such case, make sure both "poster" field as well as "poster_name", "poster_slug" and "poster_ip" fields are grouped together.


Avoid Unmeaningful Names
------------------------

Whenever possible avoid naming fields representing relation to "User" model "user". Preffer more descriptive names like "poster", "last_editor", or "giver".

For same reason avoid using "date" or "ip" as field names. Use more descriptive "posted_on" or "poster_ip" instead.


True/False Fields
-----------------

For extra clarity prefix fields representing true/false states of model with "is". "is_deleted" is better than "deleted".


URLConfs
========

Link Parameters
---------------

Links pointing at classes instead of functions should use lowercase letters and undersores. This means that link pointing at "ForumThreads" should be named "forum_threads".

If link parameters represent model fields, name them using model_field scheme. This means that if your link contains UserWarn's id and slug, name those parameters userwarn_id and userwarn_slug in your link and view.

.. note::
   Notice that paramerter for this model is `userwarn_slug`, not `user_warn_slug`. This is important because when model slug validation fails, Misago error handler seeks for lowercase class name in link parameters.

In rare cases you may want link parameters point at two instances of same model. If this is the case add use more descriptive prefix instead of one from model name (ergo "quoted_post").


Views and Forms
===============

Depending on number of views in your app, you may have single "views.py" file (AKA python module), or "views" directory (AKA python package). While both approaches are perfectly valid, you should preffer first one and only switch to latter when your views module becomes too big. Same practice applies for "forms.py". Split it only when file becomes to big to be easily navigate.

In addition to views and forms definitions, those files can also contain helper functions and attributes. Your views may perform same logic that you may want to move to single decorator or mixin in order to DRY your code while your forms may define factories or dynamic default values. However file contents should always follow "what it says on the tin" rule. If your views module defines forms or has nothing else but mixins or decorators that are imported by other modules, it shouldn't be named "views".

.. note::
   This rule is not specific just for views and forms files or even for python language ans is widely considered as good practice in majority of programming languages out there.


View Arguments
--------------

As convention, declare view arguments in order they are being used in view's code. Most common example of this is pk being declared before slug, as view has to get model from database before it validates its slug.


Templates
=========

.. note::
   There is no silver bullet approach to how you should name or organize templates in your apps. Instead in this chapter will explain convention used by Misago.


If you are looking for template file, first you should pick correct directory to search in. Misago groups templates by special "spaces" they belong to. This means "misago" directory has three subdirectories:

- admin
- emails
- forum

After you have opened right directory, you should see list of directories and html files. See which directory or file name relates most to the page you are looking to modify. Directories are used to group related templates together and may either represent part of site (like user control panel) or single view that was split into few building blocks to remove complexity from templates (like thread view that includes additional templates).

This means that some exploring will be needed, but Misago is not going to leave you on your own here. Debug mode makes Misago expose lots of inside information to help developers understand whats happening under the hood. After you enable it, Misago will wrap every rendered template in HTML comments pointing you to source files you have to look at.

.. warning::
   Never EVER EVER run your site with DEBUG = True in production. Sooner or later something will go wrong, and when it does, this will make Misago happily expose confidential details about your site's configuration to those who shouldn't see it.

   Because implementation details of Misago features are freely available on internet and safety of some of those depends on their configuration remaining secret, this will open your site for many different attacks.
