(function($) {
    if ((typeof window.simplemanagement) === "undefined") {
        window.simplemanagement = {};
    }
    var sm = window.simplemanagement;
    if ((typeof sm.compass) === "undefined") {
        sm.compass = {};
    }
    var compass = sm.compass;

    compass.Project = function(app, data) {
        this.app = app;
        this.id = ko.observable(data.id);
        this.name = ko.observable(data.name);
        this.status = ko.observable(data.status);
        this.active = ko.observable(data.active);
        this.customer = ko.observable(data.customer);
        this.priority = ko.observable(data.priority);
        this._people = ko.observable(null);
        this.effort = ko.observable(null);
        this.end = ko.observable(null);
        this.iterations = ko.observableArray([]);
        this.stage = ko.observable(0);
        if(this.active()) {
            this._people(data.people);
            if((typeof data.effort) !== "undefined")
                this.effort(data.effort);
            if((typeof data.end) !== "undefined")
                this.end(new Date(data.end));
            this.stage(1);
        }
        this.people = ko.computed(this.getPeople, this);
    };

    compass.Project.prototype = {
        getPeople: function() {
            var i, l, role, user_id, user_data;
            var people_map = this._people();
            var people = [];
            for(role in people_map) {
                for(i=0, l=people_map[role].length; i<l; i++) {
                    user_id = people_map[role][i];
                    if((typeof this.app._people[user_id] !== "undefined")) {
                        user_data = this.app._people[user_id];
                        people.push({
                            'id': user_id,
                            'avatar': user_data['avatar'],
                            'role_id': role,
                            'role': this.app.roles[role]['shortname']
                        });
                    }
                }
            }
            return people;
        },
        load: function() {
            var self = this;
            $.ajax({
                dataType: "json",
                url: this.urls.project.get,
                data: { id: this.id },
                success: function(data, status, request) {
                    var i, l;
                    self.people(data.people);
                    if((typeof data.end) !== "undefined")
                        self.end(data.end);
                    for(i=0, l=data.iterations.length; i<l; i++) {
                        self.iterations.push(data.iterations[i]);
                    }
                    self.stage(2);
                }
            });
        }
    };

    compass.Main = function(roles, people, urls) {
        this.roles = roles;
        this._people = people;
        this.urls = urls;
        this.people_filter = ko.observable('');
        this.shown_people = ko.computed(this.getShownPeople, this);
        this.active_projects = ko.observableArray([]);
        this.inactive_projects = ko.observableArray([]);
        this.loaded = ko.observable(false);
        this.messages = ko.observableArray([]);
    };

    compass.Main.prototype = {
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
                url: this.urls.projects.get,
                success: function(data, status, request) {
                    var i, l, project;
                    for(i=0, l=data.length; i<l; i++) {
                        project = data[i];
                        if(project.active)
                            self.active_projects.push(
                                new compass.Project(self, project));
                        else
                            self.inactive_projects.push(
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
                $.parseJSON(element.attr('data-urls')));
            app.load();
            compass.apps.push(app);
            ko.applyBindings(app, this);
        });
    });

})(jQuery);
