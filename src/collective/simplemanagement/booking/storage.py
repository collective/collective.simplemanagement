#-*- coding: utf-8 -*-

import uuid
from collections import Sequence

from persistent import Persistent
from BTrees.OOBTree import OOBTree
from BTrees.IOBTree import IOBTree
# from BTrees.IFBTree import IFBucket
# from BTrees.IFBTree import IFSet
from BTrees.IFBTree import weightedUnion
# from BTrees.IFBTree import weightedIntersection
from zope.interface import implementer
from zope.event import notify
from zope.index.interfaces import IIndexSort

from ..interfaces import IBooking
from ..interfaces import IBookingStorage
from .content import Booking
from .catalog import setup_catalog
from .catalog import prepare_query
from .catalog import is_keyword_index
from .events import BookingAddedEvent


def _get_next_uid():
    return uuid.uuid1().hex


class GeneratorWrapper(object):

    __slots__ = ('generator', 'stack', 'stack_length')

    def __init__(self, generator):
        self.generator = generator
        self.stack = []
        self.stack_length = 0

    def _accumulate(self):
        self.stack.append(next(self.generator))
        self.stack_length += 1

    def get(self, index):
        if index >= self.stack_length:
            while self.stack_length <= index:
                try:
                    self._accumulate()
                except StopIteration:
                    raise IndexError(index)
        return self.stack[index]


class BookingResults(Sequence):

    def __init__(self, parent, query, start=0, limit=None,
                 sort_on=None, reverse=False):
        self.parent = parent
        self.query = query
        self.sort_on = sort_on
        self.start = start if start else 0
        self.limit = limit
        self.reverse = reverse
        self._results = None
        self._sorted_results = None

    def _merge(self, op, sets):
        assert len(sets) > 1
        weight, merged = op(sets[0], sets[1])
        for set_ in sets:
            weight, merged = op(merged, set_)
        return weight, merged

    def _query(self):
        parent = self.parent
        results = []
        if self.query is None or len(self.query) == 0:
            results = parent.mapping
        else:
            query = prepare_query(parent.catalog, self.query)

            multiple_query = []
            for key, value in query.iteritems():
                if is_keyword_index(parent.catalog, key) and len(value) > 1:
                    for v in value:
                        partial_query = query.copy()
                        partial_query[key] = v
                        partial_results = parent.catalog.apply(partial_query)
                        multiple_query.append(partial_results)
            if multiple_query:
                results = self._merge(weightedUnion, multiple_query)[1]
            else:
                results = parent.catalog.apply(query)
        return results

    @property
    def results(self):
        if self._results is None:
            self._results = self._query()
        return self._results

    @property
    def sorted_results(self):
        if self._sorted_results is None:
            results = iter(self._results)
            if self.sort_on is not None:
                sort_index = self.parent.catalog[self.sort_on]
                if IIndexSort.providedBy(sort_index):
                    results = sort_index.sort(results, reverse=self.reverse)
            self._sorted_results = GeneratorWrapper(results)
        return self._sorted_results

    def __getitem__(self, index_or_slice):
        results = self.results
        results_length = len(results)
        if isinstance(index_or_slice, slice):
            start, stop, step = index_or_slice.indices(len(self))
            start = start + self.start
            stop = stop + self.start
            slice_ = []
            for i in xrange(start, stop, step):
                slice_.append(
                    self.parent.catalog_id_to_object(
                        self.sorted_results.get(i)
                    )
                )
            return slice_
        limit = self.limit
        if limit is None:
            limit = results_length
        if index_or_slice < 0:
            index = limit + index_or_slice
        else:
            index = self.start + index_or_slice
        if index >= limit:
            raise IndexError(index_or_slice)
        return self.parent.catalog_id_to_object(
            self.sorted_results.get(index)
        )

    def __len__(self):
        full_length = len(self.results)
        if self.limit is not None:
            full_length = min(full_length, self.limit)
        return full_length - self.start


@implementer(IBookingStorage)
class BookingStorage(Persistent):

    def __init__(self):
        self.bookings = OOBTree()
        # we need real randomness for object keys
        # but we cannot use the same uid for zope.catalog ids
        # because it does not support 128bit integers
        # (and we do not like to use zope.intid).
        # So, we use different keys for storage and catalog
        # and we store mapping between them here.
        self.mapping = IOBTree()
        self.catalog = setup_catalog()

    def __len__(self):
        """Returns the number of bookings.
        """
        return len(self.bookings)

    def __contains__(self, uid):
        return uid in self.bookings

    def __getitem__(self, uid):
        return self.bookings[uid]

    def __iter__(self):
        for x in self.bookings.values():
            yield x

    def add(self, booking):
        assert IBooking.providedBy(booking)
        if not booking.uid:
            # maybe we are not using `create` method
            booking.uid = self._get_next_uid()
            booking.cat_id = self._get_next_cat_id()

        self.bookings[booking.uid] = booking
        self.index(booking)
        notify(BookingAddedEvent(booking))
        return booking.uid

    def delete(self, uid):
        booking = self.bookings.pop(uid)
        self.unindex(booking)

    def create(self, **values):
        booking = Booking(**values)
        self.add(booking)
        return booking

    def _get_next_uid(self):
        return _get_next_uid()

    def _get_next_cat_id(self):
        # we know that this id may not be unique
        # but we can reindex bookings if needed
        try:
            return self.mapping.maxKey() + 1
        except ValueError:
            # no keys yet
            return 1

    def catalog_id_to_object(self, cat_id):
        uid = self.mapping[cat_id]
        return self.bookings[uid]

    def index(self, booking):
        self.catalog.index_doc(booking.cat_id, booking)
        self.mapping[booking.cat_id] = booking.uid

    def unindex(self, booking):
        self.catalog.unindex_doc(booking.cat_id)
        self.mapping.pop(booking.cat_id)
        booking.cat_id = None

    def reindex(self, booking):
        self.catalog.unindex_doc(booking.cat_id)
        self.catalog.index_doc(booking.cat_id, booking)

    def reindex_catalog(self):
        self.mapping.clear()
        self.catalog.clear()
        for booking in self.bookings:
            booking.cat_id = self._get_next_cat_id()
            self.index(booking)

    def query(self, query=None, start=0, limit=None,
              sort_on=None, reverse=False):
        """Searches for bookings.

        Returns an ordered set of ``IBooking`` objects, which match ``query``.
        ``query`` is a dictionary with the keys being field names
        or keys contained in ``references``,
        and the values either a specific value
        or a range in the form of a ``(to, from)`` tuple
        (with ``None`` being no limit).

        ``start`` and ``limit`` can be used to slice the result set.
        """
        return BookingResults(
            self,
            query,
            start=start,
            limit=limit,
            sort_on=sort_on,
            reverse=reverse
        )

    def vocabulary(self, name):
        """Returns the list of values for the given index.
        """
        # pylint: disable=protected-access
        return self.catalog[name]._fwd_index.keys()

