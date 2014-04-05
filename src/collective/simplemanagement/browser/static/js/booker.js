/*global window, jQuery, document, String */
(function ($) {
    "use strict";

    if (window.simplemanagement === undefined) {
        window.simplemanagement = {};
    }

    var sm = window.simplemanagement;

    sm.Booker = function(element) {
        this.$root = $(element);
        this.$root.parent().css({ position: 'relative' });
        this.font_size = (
            this.$root.innerWidth() / parseInt(this.$root.attr('size'), 10));
        this.name = this.$root.attr('name');
        this.$hidden = $('<input type="hidden" />');
        this.$hidden.attr('name', this.name+'.parsed');
        this.$hidden.insertAfter(this.$root);
        this.$dropdown = $('<div class="booker-dropdown">'+
                           '<div class="wrapper" /></div>');
        this.$dropdown.insertAfter(this.$root);
        this.$dropdown.hide();
        this.$dropdown.css({
            position: 'absolute'
        });
        this.electric_chars = $.parseJSON(
            this.$root.attr('data-electric-chars'));
        this.valid_chars = /[\w\-\.]/;
        this.autocomplete_url = this.$root.attr('data-autocomplete-url');
        this.autocomplete_cache = {};
        this.autocomplete_values = [];
        this.autocomplete_selected = 0;
        this.stream = [];
        this.token = null;
        this.init();
    };

    sm.Booker.prototype = {
        add: function(item) {
            var i, l, replace = null, value = this.$root.val();
            for(i=0, l=this.stream.length; i<l; i++) {
                if((this.token[2] >= this.stream[i].start &&
                        this.token[2] < this.stream[i].end) ||
                   (this.token[3] >= this.stream[i].start &&
                        this.token[3] < this.stream[i].end) ||
                   (this.token[2] <= this.stream[i].start &&
                        this.token[3] >= this.stream[i].end))
                {
                    replace = i;
                }
            }
            if(replace !== null)
                this.stream.splice(replace, {
                    portal_type: item.portal_type,
                    uuid: item.uuid,
                    start: this.token[2],
                    end: this.token[3]
                });
            else
                this.stream.push({
                    portal_type: item.portal_type,
                    uuid: item.uuid,
                    start: this.token[2],
                    end: this.token[3]
                });
            this.stream.sort(function(a, b) {
                if(a.start < b.start) return -1;
                if(a.start > b.start) return 1;
                return 0;
            });
            this.$root.val(
                value.substr(0, this.token[2]) +
                    this.token[0] + item.id +
                    value.substr(this.token[3], value.length));
            this.$root.caret(this.token[2] + item.id.length + 1);
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
                                ' <span class="sep">/</span>')).
                            appendTo($item);
                    $wrapper.append($item);
                }
            }
        },
        autocomplete: function(method) {
            var value, selected, values, values_length, selection,
                self = this;
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
                        else {
                            this.$root.val(
                                value.substr(0, this.token[2]) +
                                    value.substr(this.token[3], value.length));
                            this.$root.caret(this.token[2]);
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
                        this.$dropdown.show();
                        this.$dropdown.css({
                            top: this.$root.height(),
                            left: this.token[2] * this.font_size
                        });
                    }
                    this.render_autocomplete();
                    this.autocomplete_get({
                        filter: JSON.stringify([
                            this.token[0],
                            this.token[1]
                        ]),
                        filter_context: JSON.stringify(this.stream)
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
            console.log([electric_char, token, s, e]);
            return [electric_char, token, s, e];
        },
        init: function() {
            var self = this;
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
                    case 9: { // tab
                        e.preventDefault();
                        break;
                    }
                    default: {
                        break;
                    }
                }
            });
            this.$root.keypress(function(e) {
                if(e.which) {
                    var position = self.$root.caret();
                    var value = self.$root.val();
                    var ch = String.fromCharCode(e.which);
                    console.log('|'+ch+'|');
                    self.token = self.tokenize(
                        value+ch,
                        position);
                    if(self.token[0] !== null)
                        self.autocomplete('reload');
                    if(self.valid_chars.exec(ch) === null)
                        self.autocomplete('close');
                }
            });
            this.$root.blur(function() {
                self.autocomplete('close');
            });
        }
    };

    sm.bookers = [];

    $(document).ready(function() {
        $('.book-widget').each(function() {
            sm.bookers.push(new sm.Booker(this));
        });
    });

}(jQuery));
