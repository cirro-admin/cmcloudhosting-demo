#!/usr/bin/env python
"""Django's command-line utility. The runtime reads DJANGO_SETTINGS_MODULE from
the setdefault line below, so keep it accurate if the project is renamed."""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "starter.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
