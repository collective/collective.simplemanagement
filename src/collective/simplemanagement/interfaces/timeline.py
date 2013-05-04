from zope.location.interfaces import ILocation


class ITimeline(ILocation):
    """Keeps a list of "snapshots" over time.

    Snapshots are the status of an item at a given time,
    in the form of condensed information about it.

    It can be thought of as a versioned, local catalog of an object.
    """

    def snapshot(context, indexes=None, insert=True):
        """Take a snapshot of the context and add it to the timeline.

        ``context`` is the adapter context, which is passed for convenience
        (as :func:`~zope.annotation.factory.factory`
        sometimes wraps the whole thing in a location proxy,
        making everything extra difficult).

        ``indexes`` can optionally restrict snapshotting just to some of them
        (``None`` means *all*).

        If ``insert`` is ``False`` the snapshot isn't inserted
        into the timeline but just returned.

        Returns the snapshot as a dictionary.
        """

    def slice(from_, to, resolution, indexes=None):
        """Produces the variation of indexes over time,
        from a given point in time (``from_``) to another one (``to``).

        ``resolution`` is a ``timedelta`` object
        that represents the resolution of the returned data serie
        (e.g. if ``resolution = timedelta(days=1)``
        all items in the returned serie will be spaced by one day).

        ``indexes`` can optionally restrict slicing to just to some of them
        (``None`` means *all*).

        Returns an iterator whose elements are 2-tuples,
        the first item being the beginning of the time slice
        and the second item being a dictionary whose keys are the indexes
        (if the index is missing for that period,
        it is not present in the dictionary) and the values the values.
        """
