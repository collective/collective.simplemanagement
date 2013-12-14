/*global window, jQuery, document, ko, alert */
(function ($) {
    "use strict";
    if ((typeof window.simplemanagement) === 'undefined') {
        window.simplemanagement = {};
    }

    var sm = window.simplemanagement,
        base = sm.base || {},
        models;

    if ((typeof sm.models) === 'undefined') {
        sm.models = {};
    }

    models = sm.models;

    models.Project = function(trigger, settings, data) {
        var self = this,
            estimate = 0,
            hours = 0,
            i;

        $.extend(this, settings);
        self.trigger = $(trigger);
        self.url = self.trigger.data('projecturl');

        self.past_iterations = ko.observableArray();
        self.current_iterations = ko.observableArray();
        self.future_iterations = ko.observableArray();

        self.show_all_iterations = ko.observable(false);

        self.title = ko.observable();
        self.description = ko.observable();
        self.warning_delta_percent = ko.observable(0);
        self.iterations = ko.computed(self.get_all_iterations, self);

        self.estimate = ko.computed(function() {
            estimate = 0;
            for (i = 0; i < self.iterations().length; i += 1) {
                estimate += self.iterations()[i].estimate();
            }
            return estimate;
        });

        self.estimate_str = ko.computed(function () {
            return base.decimal2timestr(self.estimate());
        });

        self.hours = ko.computed(function() {
            hours = 0;
            for (i = 0; i < self.iterations().length; i += 1) {
                hours += self.iterations()[i].hours();
            }
            return hours;
        });

        self.hours_str = ko.computed(function () {
            return base.decimal2timestr(self.hours());
        });

        self.difference = ko.computed(function () {
            return self.estimate() - self.hours();
        });

        self.difference_str = ko.computed(function () {
            return base.decimal2timestr(self.difference());
        });

        self.time_status = ko.computed(self.get_time_status, self);

        if (data !== undefined) {
            self.url(data.url);
            self.title(data.title);
        } else {
            self.load(self.url);
        }

    };

    models.Project.prototype = {

        get_all_iterations: function () {
            var iterations = [];
            return iterations.concat(
                this.past_iterations(),
                this.current_iterations(),
                this.future_iterations()
            );
        },

        get_time_status: function () {
            // return a string representing a time status
            // of this story
            return base.get_difference_class(
                this.estimate(),
                this.hours(),
                this.warning_delta_percent()
            );
        },

        load: function () {
            var self = this;
            $.getJSON(self.url + '/json/view', function(data) {
                self.past_iterations(self.load_iterations(data.iterations.past));
                self.current_iterations(self.load_iterations(data.iterations.current));
                self.future_iterations(self.load_iterations(data.iterations.future));
                self.title(data.title);
            });
        },

        load_iterations: function (data) {
            return $.map(
                data,
                function(item) {
                    return new models.Iteration(null, {}, item);
                }
            );
        },

        save: function (data) {
            alert("save" + data);
        },

        update: function () {
            alert("update");
        }
    };

    models.Iteration = function(trigger, settings, data) {
        var self = this,
            today = new Date(),
            estimate = 0,
            hours = 0,
            i;

        self.url = null;
        $.extend(this, settings);
        if ((typeof trigger) !== 'undefined') {
            self.trigger = $(trigger);
            self.url = self.trigger.data('iterationurl');
        }

        self.messages = ko.observable();
        self.stories = ko.observableArray();
        self.status = ko.observable();
        self.title = ko.observable();
        self.description = ko.observable();
        self.start = ko.observable();
        self.end = ko.observable();

        self.can_edit = ko.observable();
        self.totals = ko.observable();
        self.details = ko.observable(false);
        self.css_class = ko.observable('open');
        self.warning_delta_percent = ko.observable(0);

        self.is_sortable = ko.observable(false);

        self.sortable_options = {
            handle: ".handle",
            tolerance: 'pointer',
            distance: 5,
            opacity: 0.5,
            revert: true
        };

        self.base_estimate = ko.observable();
        self.estimate = ko.computed({
            read: function() {
                estimate = 0;
                if (self.base_estimate()) {
                    estimate = self.base_estimate();
                } else {
                    for (i = 0; i < self.stories().length; i += 1) {
                        estimate += self.stories()[i].estimate();
                    }
                }
                return estimate;
            },
            write: function(value) {
                self.base_estimate(value);
            }
        });

        self.estimate_str = ko.computed(function () {
            return base.decimal2timestr(self.estimate());
        });

        self.base_hours = ko.observable();
        self.hours = ko.computed({
            read: function() {
                hours = 0;
                if (self.base_hours()) {
                    hours = self.base_hours();
                } else {
                    for (i = 0; i < self.stories().length; i += 1) {
                        hours += self.stories()[i].resource_time();
                    }
                }
                return hours;

            },
            write: function(value) {
                self.base_hours(value);
            }
        });

        self.hours_str = ko.computed(function () {
            return base.decimal2timestr(self.hours());
        });

        self.time_status = ko.computed(self.get_time_status, self);

        self.is_current = ko.computed(function() {

            if ((typeof self.start()) === "undefined" ||
                    (typeof self.end()) === "undefined") {
                return false;
            } else {
                // iteration.end >= today and iteration.start <= today
                if (new Date(self.end()) >= today &&
                        new Date(self.start()) <= today) {
                    return true;
                }
                return false;
            }
        });


        self.is_past = ko.computed(function() {
            if ((typeof self.start()) === "undefined") {
                return false;
            } else {
                // iteration.end >= today and iteration.start <= today
                if (new Date(self.end()) <= today) {
                    return true;
                }
                return false;
            }
        });

        self.is_future = ko.computed(function() {
            // iteration.end >= today and iteration.start <= today
            if (!(self.is_past() || self.is_current())) {
                return true;
            }
            return false;
        });

        self.toggleDetails = function () {
            if (self.details() === true) {
                self.details(false);
                self.css_class('open');
            } else {
                self.populate();
                self.details(true);
                self.css_class('close');
            }
        };

        if (data !== undefined) {
            self.url = data.url;
            self.status(data.status);
            self.title(data.title);
            self.end(data.end);
            self.start(data.start);
            self.is_sortable(data.is_sortable);
            self.can_edit(data.can_edit);
            self.warning_delta_percent(data.warning_delta_percent);

            self.estimate(data.totals.estimate);
            self.hours(data.totals.hours);

            if ((typeof data.stories) !== 'undefined') {
                self.stories(self.load_stories(data.stories));
            }

        } else {
            self.load(self.url);
        }

    };

    models.Iteration.prototype = {

        get_time_status: function () {
            // return a string representing a time status
            // of this story
            return base.get_difference_class(
                this.estimate(),
                this.hours(),
                this.warning_delta_percent()
            );
        },

        save: function (data) {
            alert("save" + data);
        },

        update: function () {
            alert("update");
        },

        load: function (url) {
            var self = this;
            $.getJSON(url + '/json/view', function(data) {
                self.stories(self.load_stories(data.stories));
                self.title(data.title);
                self.is_sortable(data.is_sortable);
            });
        },

        load_stories: function (data) {
            var iteration = this;
            return $.map(
                data,
                function(item) {
                    return new models.Story(iteration, item);
                }
            );
        },

        addStory: function (form_element) {
            var self = this,
                form = $(form_element);

            self.messages('');
            $.post(
                form.attr('action'),
                form.serialize(),
                function(data) {
                    if ((typeof data.error) !== 'undefined' &&
                            data.error !== false) {
                        self.messages(data.messages);
                    } else {
                        self.stories.push(new models.Story(self, data));
                    }
                }
            );
        },

        updateStoryPosition: function (event) {
            var item_id = event.item.id(),
                index = event.targetIndex,
                url = event.item.iteration.url;

            $.getJSON(
                url + '/story_move?story_id=' + item_id + '&new_position=' + index,
                function(data) {
                    if (data.success === false) {
                        sm.messages.addMessage({
                            type: 'error',
                            message: data.error
                        }, true);
                    }
                }
            );

        },

        removeStory: function (story) {
            this.stories.remove(story);
        }

    };

    models.StoryAction = function (story, data) {
        var self = this;

        self.story = story;
        self.title = data.title;
        self.description = data.description;
        self.css = data.css;
        self.name = data.name;
        self.href = data.href;
        self.type = data.type;
        self.action = function () {
            return self.story[self.name];
        };
    };


    models.Story = function(iteration, data) {
        var self = this;

        self.omit_keys = ["actions", "time_status"];

        self.iteration = iteration;
        self.id = ko.observable(data.id);
        self.title = ko.observable(data.title);
        self.description = ko.observable(data.description);
        self.status = ko.observable(data.status);
        self.url = ko.observable(data.url);
        self.actions = ko.observableArray(self.load_actions(data.actions));
        self.assignees = ko.observableArray(data.assignees);
        self.estimate = ko.observable(data.estimate);
        self.resource_time = ko.observable(data.resource_time);

        self.time_status = ko.computed(self.get_time_status, self);

        self.estimate_str = ko.computed(function() {
            return base.decimal2timestr(self.estimate());
        });
        self.resource_time_str = ko.computed(function() {
            return base.decimal2timestr(self.resource_time());
        });

        self.actionTemplate = function (action) {
            return 'template-' + action.type;
        };
    };

    models.Story.prototype = {
        get_time_status: function () {
            // return a string representing a time status
            // of this story
            return base.get_difference_class(
                this.estimate(),
                this.resource_time(),
                this.iteration.warning_delta_percent()
            );
        },

        load: function () {
            var self = this,
                key;

            $.getJSON(self.url() + '/json/view', function(data) {
                for (key in data) {
                    // don't update actions
                    if (self.hasOwnProperty(key) && self.omit_keys.indexOf(key) === -1) {
                        self[key](data[key]);
                    }
                }
            });
        },

        load_actions: function (data) {
            var story = this;

            return $.map(
                data,
                function(item) {
                    return new models.StoryAction(story, item);
                }
            );
        },

        save: function (data) {
            alert("save" + data);
        },

        update: function (data) {
            var self = this,
                key;
            for (key in data) {
                if (self.hasOwnProperty(key) && self.omit_keys.indexOf(key) === -1) {
                    self[key](data[key]);
                }
            }
        },

        remove: function () {
            this.iteration.removeStory(this);
        }
    };

}(jQuery));
