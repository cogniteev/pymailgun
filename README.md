pymailgun
=========

A simple mailgun client

Installation
============

```
pip install pymailgun
```

Usage
=====

To create a mailgun Client you will need a mailgun api key and the domain name
to use (must match the domain name registered on the mailgun website).

``` python
from pymailgun import Client

mailgun_client = Client({api_key}, {domain_name})
```

Features
========

To send an email

``` python

mailgun_client.send_mail(...) #see send_mail docstring
```
