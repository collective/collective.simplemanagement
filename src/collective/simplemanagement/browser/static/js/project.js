/*global window, jQuery, document, ko, alert */
(function ($) {
    "use strict";
    if ((typeof window.simplemanagement) === 'undefined') {
        window.simplemanagement = {};
    }

    var sm = window.simplemanagement,
        // base = sm.base || {},
        models;

    if ((typeof sm.models) === 'undefined') {
        sm.models = {};
    }

    models = sm.models;


    $.fn.extend({
        projectView: function (options) {
            return this.each(function () {

                var settings = $.extend(true, {}, options),
                    $this = $(this),
                    data = $this.data('project'),
                    project;

                // If the plugin hasn't been initialized yet
                if (!data) {
                    // Activates knockout.js
                    project = new models.Project(this, settings);
                    ko.applyBindings(project, this);

                    $(this).data('project', {
                        target: $this,
                        project: project
                    });
                }
            });
        }
    });

}(jQuery));

