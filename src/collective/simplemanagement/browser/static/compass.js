(function($) {
    if ((typeof window.simplemanagement) === "undefined") {
        window.simplemanagement = {};
    }
    var sm = window.simplemanagement;
    if ((typeof sm.compass) === "undefined") {
        sm.compass = {};
    }
    var compass = sm.compass;

    compass.format = function(format, data) {
        return format.replace(/\{([a-zA-Z_0-9]+)\}/g,
                              function(a, g1) { return data[g1]; });
    };

    var f = compass.format;

    compass.Project = function(app, data) {
        var i, l, item;
        this.app = app;
        this.id = ko.observable(data.id);
        this.name = ko.observable(data.name);
        this.status = ko.observable(data.status);
        this.active = ko.observable(data.active);
        this.customer = ko.observable(data.customer);
        this.priority = ko.observable(data.priority);
        this.effort = ko.observable(parseFloat(data.effort));
        this.notes = ko.observable(data.notes);
        this._people = ko.observableArray([]);
        for(i=0, l=data.people.length; i<l; i++) {
            item = data.people[i];
            item.effort = parseFloat(item.effort);
            this._people.push(item);
        }
        this.people = ko.computed(this.getPeople, this);
        this.css_class = ko.computed(function() {
            return 'status-indicator state-' + this.status();
        }, this);
    };

    compass.Project.prototype = {
        getPeople: function() {
            var i, l, role, user_id, user_data;
            var raw_people = this._people();
            var people = [];
            for(i=0, l=raw_people.length; i<l; i++) {
                user_id = raw_people[i]['id'];
                role = raw_people[i]['role'];
                if((typeof this.app._people[user_id] !== "undefined")) {
                    user_data = this.app._people[user_id];
                    people.push({
                        'id': user_id,
                        'avatar': user_data['avatar'],
                        'role_id': role,
                        'role': this.app.roles[role]['shortname'],
                        'effort': raw_people[i]['effort']
                    });
                }
            }
            return people;
        }
    };

    compass.Main = function(roles, people, base_url, plan_weeks,
                            translations) {
        this.roles = roles;
        this._people = people;
        this.base_url = base_url;
        this.plan_weeks = ko.observable(plan_weeks);
        this.translations = translations;
        this.people_filter = ko.observable('');
        this.plan_weeks_human = ko.computed(this.getFormattedWeeks, this);
        this.plan_end = ko.computed(this.getPlanEnd, this);
        this.shown_people = ko.computed(this.getShownPeople, this);
        this.active_projects = ko.observableArray([]);
        this.loaded = ko.observable(false);
        this.messages = ko.observableArray([]);
    };

    compass.Main.prototype = {
        url: function(method) {
            return this.base_url + method;
        },
        translate: function(id) {
            return this.translations[id];
        },
        getPlanEnd: function() {
            var weeks = this.plan_weeks();
            var today = new Date();
            var end = new Date(today.getTime() + (weeks*7*24*60*60*1000));
            // TODO: maybe we can format this better
            return end.toLocaleDateString();
        },
        getFormattedWeeks: function() {
            var weeks = this.plan_weeks();
            return compass.format(
                this.translate(weeks > 1 ? 'weeks' : 'week'),
                { 'week': weeks }
            );
        },
        getShownPeople: function() {
            var f_id, f_name;
            var people = [];
            var filter = this.people_filter().toLowerCase();
            for(var id in this._people) {
                f_id = id.toLowerCase();
                f_name = this._people[id]['name'].toLowerCase();
                if(filter === '' ||
                    f_id.indexOf(filter) !== -1 ||
                    f_name.indexOf(filter) !== -1) {
                    people.push({
                        'id': id,
                        'name': this._people[id]['name'],
                        'avatar': this._people[id]['avatar']
                    });
                }
            }
            return people;
        },
        load: function() {
            var self = this;
            $.ajax({
                dataType: "json",
                url: this.url('get_projects'),
                success: function(data, status, request) {
                    var i, l, project;
                    for(i=0, l=data.length; i<l; i++) {
                        project = data[i];
                        self.active_projects.push(
                            new compass.Project(self, project));
                    }
                    self.loaded(true);
                }
            });
        }
    };

    compass.apps = [];

    $(document).ready(function() {
        $('.compassview').each(function() {
            var element = $(this);
            var app = new compass.Main(
                $.parseJSON(element.attr('data-roles')),
                $.parseJSON(element.attr('data-people')),
                element.attr('data-base-url'),
                $.parseJSON(element.attr('data-plan-weeks')),
                $.parseJSON(element.attr('data-translations')));
            app.load();
            compass.apps.push(app);
            ko.applyBindings(app, this);
        });
    });

})(jQuery);
