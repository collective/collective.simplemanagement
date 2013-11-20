(function($) {
    if ((typeof window.simplemanagement) === "undefined") {
        window.simplemanagement = {};
    }
    var sm = window.simplemanagement;
    var base = sm.base || {};
    if ((typeof sm.messages) === "undefined") {
        sm.messages = {};
    }
    var messages = sm.messages;

    messages.Messages = function(element) {
        var timeout, messages, kind, i, l;
        this.$messages = $(element);
        timeout = this.$messages.attr('data-timeout');
        if(timeout)
            timeout = parseInt(timeout, 10);
        else
            timeout = 6;
        this.message_timeout = timeout;
        this.transient_messages = ko.observableArray([]);
        this.permanent_messages = ko.observableArray([]);
        messages = this.$messages.attr('data-messages');
        if(messages)
            messages = $.parseJSON(messages);
        else
            messages = {
                'transient': [],
                'permanent': []
            };
        for(kind in messages) {
            for(i=0, l=messages[kind].length; i<l; i++) {
                this.addMessage(messages[kind][i], (kind === 'permanent'));
            }
        }
        this.has_messages = ko.computed(this.hasMessages, this);
    };

    messages.Messages.prototype = {
        hasMessages: function() {
            return (this.transient_messages().length > 0 ||
                    this.permanent_messages().length > 0);
        },
        addMessage: function(message, permanent) {
            var index, self = this;
            if(permanent) {
                this.permanent_messages.push(message);
            }
            else {
                this.transient_messages.push(message);
                index = this.transient_messages().length - 1;
                message.timeout_id = window.setTimeout(
                    function() {
                        self.transient_messages.splice(index, 1);
                    },
                    this.message_timeout * 1000);
            }
        },
        dismissMessage: function(index, permanent) {
            var message;
            if(permanent) {
                this.permanent_messages.splice(index, 1);
            }
            else {
                message = this.transient_messages.splice(index, 1);
                window.clearTimeout(message.timeout_id);
            }
        }
    };

    messages.main = null;

    messages.addMessage = function(message, permanent) {
        if(messages.main)
            messages.main.addMessage(message, permanent);
    };

    $(document).ready(function() {
        var $messages = $('#portal-ko-messages');
        if($messages.length > 0) {
            messages.main = new messages.Messages($messages);
            ko.applyBindings(messages.main, $messages.get(0));
        }
    });

})(jQuery);
