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

        self.iterations = ko.observableArray();
        self.title = ko.observable();
        self.description = ko.observable();

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

        if (data !== undefined) {
            self.url(data.url);
            self.title(data.title);
        } else {
            self.load(self.url);
        }

    };

    models.Project.prototype = {

        load: function () {
            var self = this,
                key;
            $.getJSON(self.url + '/json/view', function(data) {
                self.iterations(self.load_iterations(data.iterations));
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

        self.stories = ko.observableArray();
        self.status = ko.observable();
        self.title = ko.observable();
        self.description = ko.observable();
        self.start = ko.observable();
        self.end = ko.observable();

        self.details = ko.observable(false);
        self.css_class = ko.observable('open');
        self.is_sortable = ko.observable(false);

        self.sortable_options = {
            handle: ".handle",
            tolerance: 'pointer',
            distance: 5,
            opacity: 0.5,
            revert: true
        };

        self.estimate = ko.computed(function() {
            estimate = 0;
            for (i = 0; i < self.stories().length; i += 1) {
                estimate += self.stories()[i].estimate();
            }
            return estimate;
        });

        self.estimate_str = ko.computed(function () {
            return base.decimal2timestr(self.estimate());
        });

        self.hours = ko.computed(function() {
            hours = 0;
            for (i = 0; i < self.stories().length; i += 1) {
                hours += self.stories()[i].resource_time();
            }
            return hours;
        });

        self.hours_str = ko.computed(function () {
            return base.decimal2timestr(self.hours());
        });

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

            if ((typeof data.stories) !== 'undefined') {
                self.stories(self.load_stories(data.stories));
            }

        } else {
            self.load(self.url);
        }

    };

    models.Iteration.prototype = {

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

        updateStoryPosition: function (event) {
            var item_id = event.item.id(),
                index = event.targetIndex,
                url = event.item.iteration.url;

            $.getJSON(
                url + '/story_move?story_id=' + item_id + '&new_position=' + index,
                function(data) {
                    if (data.success === false) {
                        alert(data.error);
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
        self.time_status = ko.observable(data.time_status);

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

        load: function () {
            var self = this,
                key;
            $.getJSON(self.url() + '/json/view', function(data) {
                for (key in data) {
                    if (self.hasOwnProperty(key)) {
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
                self[key](data[key]);
            }
        },

        remove: function () {
            this.iteration.removeStory(this);
        }
    };

}(jQuery));
