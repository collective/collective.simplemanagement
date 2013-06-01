(function($) {
    if ((typeof window.simplemanagement) === "undefined") {
        window.simplemanagement = {};
    }
    var sm = window.simplemanagement;
    if ((typeof sm.compass) === "undefined") {
        sm.compass = {};
    }
    var compass = sm.compass;

    compass.Users = function(data) {
        this._data = data;
    };

    compass.Project = function(options) {
    };

    compass.Projects = function(data) {
        this._data = data;
    };

})(jQuery);
