import functools
import inspect
import logging

from cachetools.keys import hashkey, methodkey


logger = logging.getLogger(__name__)


class NullContext(object):
    """A class for noop context managers."""

    def __enter__(self):
        """Return ``self`` upon entering the runtime context."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Raise any exception triggered within the runtime context."""

    async def __aenter__(self):
        """Return ``self`` upon entering the runtime context."""
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Raise any exception triggered within the runtime context."""


def aiocached(cache, key=hashkey, lock=None):
    """Decorator to wrap a function or a coroutine with a memoizing callable.

    When ``lock`` is provided for a standard function, it's expected to
    implement ``__enter__`` and ``__exit__`` that will be used to lock
    the cache when it gets updated. If it wraps a coroutine, ``lock``
    must implement ``__aenter__`` and ``__aexit__``.

    Example:
    >>> import asyncio
    >>> from service_base.api import aiocached
    >>> i = 1
    >>> @aiocached(cache={})
    ... async def get_camera(camera_id):
    ...     global i
    ...     i += 1
    ...     return camera_id + i
    >>> async def print_camera():
    ...     print(await get_camera(20))
    ...     print(await get_camera(20))
    ...     print(await get_camera(30))
    >>> asyncio.run(print_camera())
    22
    22
    33
    """
    lock = lock or NullContext()

    def decorator(func):
        if not inspect.iscoroutinefunction(func):
            raise RuntimeError("Use aiocached only with async functions")

        async def wrapper(*args, **kwargs):
            fk = key(*args, **kwargs)
            async with lock:
                fval = cache.get(fk)
            # cache hit
            if fval is not None:
                return fval
            # cache miss
            fval = await func(*args, **kwargs)
            try:
                async with lock:
                    cache[fk] = fval
            except ValueError:
                logger.debug("Failed to cache {0}".format(fval))
            return fval

        return functools.wraps(func)(wrapper)

    return decorator


def aiocachedmethod(cache, key=methodkey, lock=None):
    """Decorator to wrap a class or instance method with a memoizing
    callable that saves results in a cache.

    adapted for asyncio from "cachedmethod" of cachetools

    Example:
    >>> import asyncio
    >>> import operator
    >>> from service_base.api import aiocachedmethod
    >>> class MyCacher:
    ...     def __init__(self):
    ...         self._cache = {}
    ...         self.i = 1
    ...     @aiocachedmethod(operator.attrgetter("_cache"))
    ...     async def get_camera(self, camera_id: int):
    ...         self.i += 1
    ...         return camera_id + self.i
    >>> async def print_camera():
    ...     cacher = MyCacher()
    ...     print(await cacher.get_camera(20))
    ...     print(await cacher.get_camera(20))
    ...     print(await cacher.get_camera(30))
    >>> asyncio.run(print_camera())
    22
    22
    33
    """

    def null(s):
        return NullContext()

    lock = lock or null

    def decorator(method):
        async def wrapper(self, *args, **kwargs):
            c = cache(self)
            if c is None:
                return method(self, *args, **kwargs)
            k = key(self, *args, **kwargs)
            try:
                with lock(self):
                    return c[k]
            except KeyError:
                pass  # key not found
            v = await method(self, *args, **kwargs)
            # in case of a race, prefer the item already in the cache
            try:
                with lock(self):
                    return c.setdefault(k, v)
            except ValueError:
                return v  # value too large

        def clear(self):
            c = cache(self)

            if c is not None:
                with lock(self):
                    c.clear()

        wrapper.cache = cache
        wrapper.cache_key = key
        wrapper.cache_lock = lock
        wrapper.cache_clear = clear

        return functools.update_wrapper(wrapper, method)

    return decorator
