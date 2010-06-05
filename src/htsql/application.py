#
# Copyright (c) 2006-2010, Prometheus Research, LLC
# Authors: Clark C. Evans <cce@clarkevans.com>,
#          Kirill Simonov <xi@resolvent.net>
#


"""
:mod:`htsql.application`
========================

This module implements an HTSQL application.
"""


from __future__ import with_statement
from .context import context
from .addon import Addon
from .adapter import AdapterRegistry
from .util import DB
from .wsgi import WSGI
import pkg_resources


class Application(object):
    """
    Implements an HTSQL application.

    `db`
        The connection URI.
    """

    def __init__(self, db, *extensions):
        # Parse the connection URI.
        self.db = DB.parse(db)
        # Generate the list of addon names.
        addon_names = []
        addon_names.append('htsql.core')
        addon_names.append('engine.%s' % self.db.engine)
        addon_names.extend(extensions)
        # Import addons from the entry point group `htsql.addons`.
        addons = []
        for name in addon_names:
            entry_points = list(pkg_resources.iter_entry_points('htsql.addons',
                                                                name))
            if len(entry_points) == 0:
                raise ImportError("unknown entry point %r" % name)
            elif len(entry_points) > 1:
                raise ImportError("ambiguous entry point %r" % name)
            entry_point = entry_points[0]
            addon_class = entry_point.load()
            if not (isinstance(addon_class, type) and
                    issubclass(addon_class, Addon)):
                raise ImportError("invalid entry point %r" % name)
            addons.append(addon_class)
        # Get adapters exported by addons.
        adapters = []
        for addon_class in addons:
            adapters.extend(addon_class.adapters)
        # TODO: these should be defined by the `htsql.core` addon.
        # Initialize the adapter registry.
        self.adapter_registry = AdapterRegistry(adapters)

    def __enter__(self):
        """
        Activates the application in the current thread.
        """
        context.switch(None, self)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        Inactivates the application in the current thread.
        """
        context.switch(self, None)

    def __call__(self, environ, start_response):
        """
        Implements the WSGI entry point.
        """
        with self:
            wsgi = WSGI()
            return wsgi(environ, start_response)

