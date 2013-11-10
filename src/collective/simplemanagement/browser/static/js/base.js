(function($, ko) {
    if ((typeof window.simplemanagement) === "undefined") {
        window.simplemanagement = {};
    }
    var sm = window.simplemanagement;
    if ((typeof sm.base) === "undefined") {
        sm.base = {};
    }
    var base = sm.base;

    // Base function to format strings.
    //
    // Works like python's .format() method:
    //
    //     >>> format('Hello {foo}', { foo: 'World' });
    //     'Hello world'
    //
    base.format = function(format, data) {
        return format.replace(/\{([a-zA-Z_0-9]+)\}/g,
                              function(a, g1) { return data[g1]; });
    };

    // Fixed box
    // A box that, once the use scrolls past it,
    // remains fixed at the top of the screen, following the scroll
    $.fn.fixedbox = function() {
        var args = Array.prototype.slice.apply(arguments, []);
        return this.each(function() {
            var element = $(this);
            var element_offset = element.offset();
            var element_width = element.outerWidth();
            $(window).scroll(function() {
                var scroll = $(window).scrollTop();
                if(scroll > element_offset.top) {
                    if(!element.attr('style'))
                        element.css({
                            position: 'fixed',
                            left: element_offset.left+'px',
                            top: '2px', // TODO: maybe leave this to CSS
                                        // via margin
                            width: element_width+'px'
                        });
                }
                else {
                    if(element.attr('style'))
                        element.removeAttr('style');
                }
            });
        });
    };

    // The jqueryDrawer binding for knockout
    //
    // TODO: kill in favour of new drawer
    ko.bindingHandlers.jqueryDrawer = {
        init: function(element, accessor) {
            var value = accessor();
            var content_id = value.content;
            var content = null;
            $(element).drawer({
                group: value.group ? value.group : null,
                content: function(callback) {
                    if(!content)
                        content = $(content_id).removeAttr('style').detach();
                    callback(content);
                },
                position: value.position ? value.position : "bottom",
                css_class: value.css_class ? value.css_class : "tooltip",
                remove: false
            });
        }
    };

    // A knockout binding to set an element as "droppable".
    //
    // Usage:
    //
    //     data-bind="droppable: { action: addPerson,
    //                             options: { scope: 'people' } }"
    //
    // do_something is called when the drop happens,
    // it will receive the following parameters:
    //
    // item
    //     the javascript object associated to the element being dragged
    // event
    //     jQuery event
    // ui
    //     jQuery UI info
    //
    // The parameter options is passed as-is to jQuery UI .droppable()
    //
    // Uses jQuery UI, cfr. http://stackoverflow.com/a/15812995/967274
    // (the responder is the creator of knockout-sortable)
    ko.bindingHandlers.droppable = {
        init: function(element, valueAccessor) {
            var value = valueAccessor() || {};
            var action = value.action || value;

            var options = {
                drop: function(event, ui) {
                    var item = ko.utils.domData.get(
                        ui.draggable[0],
                        "ko_dragItem");

                    if (item) {
                        item = item.clone ? item.clone() : item;
                        action.call(this, item, event, ui);
                    }
                }
            };
            $.extend(options, value.options || {});

            $(element).droppable(options);
        }
    };

    // Knockout binding for infinite scrolling
    //
    // Usage (on the scrollable list wrapper):
    //
    //     data-bind="scrollBottom: function() { do_something(); }"
    //
    // When the scrolling hits the bottom do_something will be called.
    ko.bindingHandlers.scrollBottom = {
        init: function(element, accessor) {
            var value = accessor();
            var unwrapped = ko.unwrap(value);
            var jq_element = $(element);
            jq_element.scroll(function() {
                var scroll, scroll_height, height;
                scroll = jq_element.scrollTop();
                scroll_height = jq_element.prop('scrollHeight');
                height = jq_element.height();
                if((scroll_height - scroll) <= height)
                    unwrapped();
            });
        }
    };

    // A "throttled" knockout observable.
    //
    // This means its value can't change more rapidly than the limit you set,
    // and any change events between "ticks" will be dropped.
    //
    // The typical use case is search boxes for which you set
    //
    //     valueUpdate: 'afterkeydown'
    //
    // But you don't want the value to be updated
    // each time the user inserts a new letter,
    // else you'll end up with a lot of useless requests.
    //
    // Example:
    //
    //     this.foo = ko.throttledObservable('', 1000);
    //
    // this.foo won't be updated more rapidly than once every second
    // even if the user is continuously typing Shakespeare's Hamlet
    // (a strong indication there might be a monkey
    // on the other side of the screen)
    //
    // http://jsfiddle.net/rniemeyer/7mGxJ/
    // I owe the guy something like ten beers
    ko.throttledObservable = function(initialValue, delay) {
        var _internal = ko.observable(initialValue);
        var _buffer = "";
        var _pending = false;

        return ko.dependentObservable({
            read: _internal,
            write: function(newValue) {
                _buffer = newValue;
                if (!_pending) {
                    _pending = true;
                    setTimeout(function() {
                        _pending = false;
                        _internal(_buffer);
                    }, delay);
                }
            }
        });
    };

})(jQuery, ko);
