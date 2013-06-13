from zope.interface import Interface

class IMassiveBookingUploader(Interface):
    """ Utility to upload booking ct """

    def uploade_event_list(self,parent=None,events=[]):
        """
        Method to create a list of booking content type
        using events list as source
        """