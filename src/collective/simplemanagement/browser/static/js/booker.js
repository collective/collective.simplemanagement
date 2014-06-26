/*global window, jQuery, document, String, XRegExp */
(function ($) {
    "use strict";

    if (window.simplemanagement === undefined) {
        window.simplemanagement = {};
    }

    var sm = window.simplemanagement;

    sm.regex_escape = function(c) {
        var hex = c.charCodeAt(0).toString(16);
        while(hex.length < 4) {
            hex = "0" + hex;
        }
        return "\u" + hex;
    };

    sm.Booker = function(element) {
        this.$root = $(element);
        this.$root.parent().css({ position: 'relative' });
        this.font_size = (
            this.$root.innerWidth() / parseInt(this.$root.attr('size'), 10));
        this.$references = $(this.$root.attr('data-references'));
        this.$tags = $(this.$root.attr('data-tags'));
        this.$dropdown = $('<div class="booker-dropdown">'+
                           '<div class="wrapper" /></div>');
        this.$dropdown.insertAfter(this.$root);
        this.$dropdown.hide();
        this.$dropdown.css({
            position: 'absolute'
        });
        this.electric_chars = $.parseJSON(
            this.$root.attr('data-electric-chars'));
        this._valid_chars = this.$root.attr('data-valid-chars');
        this.valid_chars = new RegExp(this._valid_chars);
        this.force_validation_chars = $.parseJSON(
            this.$root.attr('data-force-validation-chars'));
        this.autocomplete_url = this.$root.attr('data-autocomplete-url');
        this.autocomplete_cache = {};
        this.autocomplete_values = [];
        this.autocomplete_selected = 0;
        this.stream = [];
        this.frozen_references = [];
        this.token = null;
        this.broken = false;
        this.init();
    };

    sm.Booker.prototype = {
        setBroken: function(value) {
            this.broken = value;
            if(value)
                this.$root.parents('form').find('input[type="submit"]').
                    attr('disabled', 'disabled');
            else
                this.$root.parents('form').find('input[type="submit"]').
                    removeAttr('disabled');
        },
        get_regex: function() {
            var c, elchars = [], regex;
            for(c in this.electric_chars) elchars.push(sm.regex_escape(c));
            regex = new RegExp('('+elchars.join('|')+')('+
                               this._valid_chars+'+)', 'g');
            return regex;
        },
        parse: function() {
            var references, raw_references, tags, item, i, l, regex,
                self = this;
            regex = this.get_regex();
            raw_references = $.parseJSON(this.$references.val() || '[]');
            references = [];
            for(i=0, l=raw_references.length; i<l; i++) {
                if(raw_references[i].frozen)
                    this.frozen_references.push(raw_references[i]);
                else
                    references.push(raw_references[i]);
            }
            tags = $.parseJSON(this.$tags.val() || '[]');
            XRegExp.forEach(this.$root.val(), regex, function(m) {
                if(self.electric_chars[m[1]] === null) {
                    item = tags.shift();
                    self.stream.push({
                        portal_type: null,
                        uuid: m[2],
                        id: m[2],
                        start: m.index,
                        end: m.index + m[0].length
                    });
                }
                else {
                    item = references.shift();
                    item.id = m[2];
                    item.start = m.index;
                    item.end = m.index + m[0].length;
                    self.stream.push(item);
                }
            });
        },
        add: function(item) {
            var i, l, replace = null, value = this.$root.val();
            if(replace !== null)
                this.stream.splice(replace, {
                    portal_type: item.portal_type,
                    uuid: item.uuid,
                    id: item.id,
                    start: this.token[2],
                    end: this.token[3]
                });
            else
                this.stream.push({
                    portal_type: item.portal_type,
                    uuid: item.uuid,
                    id: item.id,
                    start: this.token[2],
                    end: this.token[3]
                });
            this.stream.sort(function(a, b) {
                if(a.start < b.start) return -1;
                if(a.start > b.start) return 1;
                return 0;
            });
            this.save_related();
            this.$root.val(
                value.substr(0, this.token[2]) +
                    this.token[0] + item.id +
                    value.substr(this.token[3], value.length));
            this.$root.caret(this.token[2] + item.id.length + 1);
        },
        save_related: function() {
            var i, l, references_values = [], tags_values = [];
            for(i=0, l=this.frozen_references.length; i<l; i++) {
                references_values.push(this.frozen_references[i]);
            }
            for(i=0, l=this.stream.length; i<l; i++) {
                if(this.stream[i].portal_type)
                    references_values.push({
                        portal_type: this.stream[i].portal_type,
                        uuid: this.stream[i].uuid
                    });
                else
                    tags_values.push(this.stream[i].id);
            }
            this.$references.val(JSON.stringify(references_values));
            this.$tags.val(JSON.stringify(tags_values));
        },
        render_autocomplete: function() {
            var i, l, $wrapper, $info, $item, item;
            $wrapper = this.$dropdown.find('.wrapper');
            $wrapper.empty();
            if(this.autocomplete_values.length === 0) {
                $info = $('<p class="no-results"></p>');
                $info.text(this.$root.attr('data-novalues'));
                $wrapper.append($info);
            }
            else {
                for(i=0, l=this.autocomplete_values.length; i<l; i++) {
                    item = this.autocomplete_values[i];
                    $item = $('<div class="item" />');
                    if(i === this.autocomplete_selected)
                        $item.addClass('selected');
                    $('<p class="title"></p>').text(item.title).
                        appendTo($item);
                    if(item.breadcrumb)
                        $('<p class="breadcrumb"></p>').html(
                            item.breadcrumb.join(
                                ' <span class="sep">/</span> ')).
                            appendTo($item);
                    $wrapper.append($item);
                }
            }
        },
        autocomplete: function(method) {
            var value, selected, values, values_length, selection, offset,
                offsetParent, self = this;
            offsetParent = this.$root.offsetParent().offset();
            offset = this.$root.offset();
            offset = {
                top: offset.top - offsetParent.top,
                left: offset.left - offsetParent.left
            };
            value = this.$root.val();
            selected = this.autocomplete_selected;
            values = this.autocomplete_values;
            values_length = this.autocomplete_values.length;
            switch(method) {
                case 'close': {
                    if(this.token !== null && this.token[0] !== null) {
                        if(values_length > 0) {
                            if(selected < values_length)
                                selection = values[selected];
                            else
                                selection = values[0];
                            this.add(selection);
                        }
                        this.token = null;
                    }
                    this.autocomplete_values = [];
                    this.autocomplete_selected = 0;
                    this.$dropdown.hide();
                    break;
                }
                case 'refresh': {
                    this.render_autocomplete();
                    break;
                }
                case 'reload': {
                    this.autocomplete_selected = 0;
                    if(!this.$dropdown.is(':visible')) {
                        this.$dropdown.css({
                            'top': (offset.top +
                                    this.$root.outerHeight()) + 'px',
                            'left': (offset.left +
                                     (this.token[2] * this.font_size)) + 'px'
                        });
                        this.$dropdown.show();
                    }
                    this.render_autocomplete();
                    this.autocomplete_get({
                        filter: JSON.stringify([
                            this.token[0],
                            this.token[1]
                        ]),
                        filter_context: JSON.stringify(this.stream),
                        frozen_refs: JSON.stringify(this.frozen_references)
                    },
                    function(data) {
                        self.autocomplete_values = data;
                        self.render_autocomplete();
                    });
                    break;
                }
                default:
                    break;
            }
        },
        autocomplete_get: function(data, callback) {
            var key = $.param(data), self = this;
            if(this.autocomplete_cache[key] !== undefined)
                callback(this.autocomplete_cache[key]);
            else {
                $.getJSON(
                    this.autocomplete_url,
                    data,
                    function(data, status, request) {
                        self.autocomplete_cache[key] = data;
                        callback(data);
                    }
                );
            }
        },
        tokenize: function(value, position) {
            var i, l, s, e, electric_char = null, token = '';
            for(i=position; i>=0; i--) {
                if(this.valid_chars.exec(value[i]) === null) {
                    if(this.electric_chars[value[i]] !== undefined)
                        electric_char = value[i];
                    break;
                }
                token = value[i] + token;
            }
            s = i;
            for(i=(position+1), l=value.length; i<l; i++) {
                if(this.valid_chars.exec(value[i]) === null)
                    break;
                token = token + value[i];
            }
            e = i;
            return [electric_char, token, s, e];
        },
        cleanup: function(force) {
            var i, l, item, regex, found, stream = [], broken = false,
                value = this.$root.val(), self = this;
            regex = this.get_regex();
            XRegExp.forEach(value, regex, function(m) {
                found = false;
                for(i=0, l=self.stream.length; i<l; i++) {
                    item = self.stream[i];
                    if(item.id === m[2]) {
                        found = true;
                        item.start = m.index;
                        item.end = m.index + m[0].length;
                        stream.push(item);
                    }
                }
                if(!found) {
                    if(self.force_validation_chars.indexOf(m[1]) == -1) {
                        // BBB: this hack is the only way to support the
                        // "do not autocomplete tags" thingie
                        // but will break if we change FORCE_VALIDATION_CHARS
                        stream.push({
                            portal_type: null,
                            uuid: m[2],
                            id: m[2],
                            start: m.index,
                            end: m.index + m[0].length
                        });
                        found = true;
                    }
                    if(!found && force) {
                        broken = true;
                    }
                }
            });
            this.setBroken(broken);
            this.stream = stream;
            this.save_related();
            if(force && broken)
                sm.messages.addMessage({
                    type: 'warning',
                    message: this.$root.attr('data-broken-message')
                }, false);
        },
        init: function() {
            var self = this;
            this.parse();
            this.$root.keydown(function(e) {
                switch(e.keyCode) {
                    case 37: // arrow back
                    case 39: { // arrow forward
                        self.autocomplete('close');
                        break;
                    }
                    case 38: { // arrow up
                        e.preventDefault();
                        if(self.$dropdown.is(':visible')) {
                            if(self.autocomplete_selected > 0)
                                self.autocomplete_selected--;
                            self.autocomplete('refresh', null);
                        }
                        break;
                    }
                    case 40: { // arrow down
                        e.preventDefault();
                        if(self.$dropdown.is(':visible')) {
                            self.autocomplete_selected++;
                            self.autocomplete('refresh', null);
                        }
                        break;
                    }
                    case 13: { // enter
                        e.preventDefault();
                        self.autocomplete('close');
                        break;
                    }
                    case 32: { // space
                        self.autocomplete('close');
                        break;
                    }
                    case 9: { // tab
                        break;
                    }
                    default: {
                        break;
                    }
                }
            });
            this.$root.keypress(function(e) {
                self.cleanup(false);
                if(e.which) {
                    var ch;
                    var position = self.$root.caret();
                    var value = self.$root.val();
                    switch(e.which) {
                        case 8: { // backspace
                            value = value.substr(0, value.length-1);
                            position = position - 2;
                            break;
                        }
                        default: {
                            ch = String.fromCharCode(e.which);
                            value = value + ch;
                            break;
                        }
                    }
                    self.token = self.tokenize(value, position);
                    if((self.valid_chars.exec(ch) !== null ||
                            e.which === 8) &&
                                self.token[0] !== null)
                        self.autocomplete('reload');
                    else
                        self.autocomplete('close');
                }
            });
            this.$root.blur(function() {
                self.autocomplete('close');
                self.cleanup(true);
            });
            this.$root.caret(this.$root.val().length);
            this.$root.parents('form').submit(function(e) {
                if(self.broken) {
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                }
            });
        }
    };

    sm.bookers = [];

    $.fn.extend({
        bookWidget: function() {
            var options = {};
            if(arguments.length > 0)
                options = arguments[0];
            return this.each(function() {
                var settings = $.extend(true, {}, options),
                    $this = $(this),
                    data = $this.data('booker'),
                    booker;
                // If the plugin hasn't been initialized yet
                if(!data) {
                    booker = new sm.Booker(this);
                    sm.bookers.push(booker);

                    $(this).data('booker', booker);
                }
            });
        }
    });

    $(document).ready(function() {
        $('.book-widget').bookWidget();
    });

}(jQuery));
