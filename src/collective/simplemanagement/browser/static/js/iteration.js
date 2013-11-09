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
        iterationView: function (options) {
            return this.each(function () {

                var settings = $.extend(true, {}, options),
                    $this = $(this),
                    data = $this.data('iteration'),
                    iteration;

                // If the plugin hasn't been initialized yet
                if (!data) {
                    // Activates knockout.js
                    iteration = new models.Iteration(this, settings);
                    ko.applyBindings(iteration);

                    $(this).data('iteration', {
                        target: $this,
                        iteration: iteration
                    });
                }
            });
        }
    });

}(jQuery));

