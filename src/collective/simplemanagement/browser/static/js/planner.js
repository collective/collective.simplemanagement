/*global window, jQuery, document, alert,
  portal_url, common_content_filter */
(function ($) {
    "use strict";

    if (window.simplemanagement === undefined) {
        window.simplemanagement = {};
    }

    var sm = window.simplemanagement;

    sm.Planner = function(element) {
        this.init(element);
    };

    sm.Planner.prototype = {
        init: function(element) {
            var self = this;
            this.element = $(element);
            this.element_id = this.element.attr('id');
            this.left_selector = $('#' + this.element_id + '-left');
            this.right_selector = $('#' + this.element_id + '-right');
            this.loadStories(this.left_selector);
            this.loadStories(this.right_selector);
            this.left_selector.change(function() {
                self.loadStories(self.left_selector);
            });
            this.right_selector.change(function() {
                self.loadStories(self.right_selector);
            });
        },

        loadStories: function(selector) {
            var self = this,
                uuid = $('option:selected', selector).val(),
                container = $('#' + selector.attr('id') + '-container');
            container.attr('data-sortable', '');
            container.empty();
            container.load(
                './@@stories',
                {
                    iteration: uuid,
                    widget_id: this.element_id
                },
                function(response, status, request) {
                    self.makeSortable(container);
                }
            );
        },

        makeSortable: function(element) {
            var self = this;
            if (element.attr('data-sortable') === 'true') {
                element.find('ul.sortable').sortable('destroy');
            }
            element.find('ul.sortable').sortable({
                update: function(event, ui) {
                    self.update(event, ui);
                },
                start: function(event, ui) {
                    if (event.ctrlKey || event.metaKey) {
                        ui.item.addClass('copy');
                    }
                },
                sort: function(event, ui) {
                    if (event.ctrlKey || event.metaKey) {
                        ui.item.addClass('copy');
                    } else {
                        ui.item.removeClass('copy');
                    }
                },
                stop: function(event, ui) {
                    ui.item.removeClass('copy');
                },
                receive: function(event, ui) {
                    var destination = $(event.target),
                        destination_uuid = destination.attr('data-uuid'),
                        origin = $(ui.sender),
                        origin_uuid = origin.attr('data-uuid');
                    if (origin_uuid === destination_uuid) {
                        $(ui.sender).sortable('cancel');
                    }
                },
                tolerance: 'pointer',
                distance: 5,
                opacity: 0.5,
                revert: true,
                connectWith: '.' + this.element_id + '-stories'
            });
            element.attr('data-sortable', 'true');
        },

        update: function(event, ui) {
            var self = this,
                destination = $(event.target),
                destination_uuid = destination.attr('data-uuid'),
                origin = $(ui.sender),
                origin_uuid = origin.attr('data-uuid'),
                story_id = ui.item.attr('data-storyid'),
                origin_url,
                destination_discreet,
                destination_url,
                copy;

            if (origin_uuid) {
                if (origin_uuid !== destination_uuid) {
                    origin_url = origin.attr('data-moveurl');
                    //console.log(story_id+': '+origin_uuid+' -> '+destination_uuid+' @ '+ui.item.index());
                    if (origin.children('li').length === 0) {
                        origin.siblings('p.discreet').show();
                    }
                    destination_discreet = destination.siblings('p.discreet');
                    if (destination_discreet.is(':visible')) {
                        destination_discreet.hide();
                    }
                    copy = 'false';
                    if (event.ctrlKey || event.metaKey) {
                        copy = 'true';
                    }
                    $.getJSON(
                        origin_url,
                        {
                            story_id: story_id,
                            new_iteration: destination_uuid,
                            new_position: ui.item.index(),
                            do_copy: copy
                        },
                        function(data) {
                            if (data.success === false) {
                                alert(data.error);
                            }
                            if (copy) {
                                self.loadStories(self.left_selector);
                                self.loadStories(self.right_selector);
                            }
                        }
                    );
                }
            } else {
                destination_url = destination.attr('data-moveurl');
                $.getJSON(
                    destination_url,
                    {
                        story_id: story_id,
                        new_position: ui.item.index()
                    },
                    function(data) {
                        if (data.success === false) {
                            alert(data.error);
                        }
                    }
                );
            }
        }
    };

    sm.planners = [];


}(jQuery));
