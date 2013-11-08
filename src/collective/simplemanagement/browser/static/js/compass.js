(function($) {
    if ((typeof window.simplemanagement) === "undefined") {
        window.simplemanagement = {};
    }
    var sm = window.simplemanagement;
    var base = sm.base || {};
    if ((typeof sm.compass) === "undefined") {
        sm.compass = {};
    }
    var compass = sm.compass;

    var f = base.format;

    compass.Person = function(project, data) {
        this.project = project;
        this.id = data.id;
        this.role = ko.observable(data.role);
        this.effort = ko.observable(data.effort);
        this.dom_id = ko.computed(this.domId, this);
        this.display_role = ko.computed(this.getDisplayRole, this);
        this.avatar = ko.computed(this.getAvatar, this);

        // TODO: in this file we are using a mix & match of approaches,
        // we should standardize
        var self = this;
        this.role.subscribe(function(value) {
            self.project.save(
                { people: [ self.toJSON() ] },
                {
                    type: 'info',
                    message: base.format(
                        self.project.app.translate('new-role'),
                        {
                            name: self.project.app._people[self.id].name,
                            project: self.project.name(),
                            role: self.project.app.roles[value].name
                        }
                    )
                }
            );
        });
        this.effort.subscribe(function(value) {
            self.project.save(
                { people: [ self.toJSON() ] },
                {
                    type: 'info',
                    message: base.format(
                        self.project.app.translate('new-effort'),
                        {
                            name: self.project.app._people[self.id].name,
                            project: self.project.name(),
                            effort: value.toString()
                        }
                    )
                }
            );
        });
    };

    compass.Person.prototype = {
        domId: function() {
            return this.project.id().replace(/\//g, '-') + '-' + this.id;
        },
        getAvatar: function() {
            return this.project.app._people[this.id].avatar;
        },
        getDisplayRole: function() {
            return this.project.app.roles[this.role()].shortname;
        },
        toJSON: function(remove) {
            var data = {
                id: this.id,
                role: this.role(),
                effort: this.effort().toString()
            };
            if(remove) data['remove'] = true;
            return data;
        }
    };

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
        this.people = ko.observableArray([]);
        for(i=0, l=data.people.length; i<l; i++) {
            item = data.people[i];
            item.effort = parseFloat(item.effort);
            this.people.push(new compass.Person(this, item));
        }
        this.css_class = ko.computed(function() {
            return 'status-indicator state-' + this.status();
        }, this);
        var self = this;
        this.effort.subscribe(function(value) {
            self.save(
                { effort: value.toString() },
                {
                    type: 'info',
                    message: base.format(
                        self.app.translate('new-project-effort'),
                        {
                            project: self.name(),
                            effort: value.toString()
                        }
                    )
                }
            );
        });
        this.notes.subscribe(function(value) {
            self.save(
                { notes: value },
                {
                    type: 'info',
                    message: self.app.translate('changes-saved')
                }
            );
        });
        this.save = function(value, message) {
            $.ajax({
                type: 'POST',
                url: self.app.url('set_project_data'),
                data: {
                    project: self.id,
                    data: window.JSON.stringify(value)
                },
                traditional: true,
                dataType: 'json',
                success: function(data, status, request) {
                    self.app.addMessage(message);
                },
                error: function(request, status, error) {
                    self.app.addMessage({
                        type: 'error',
                        message: base.format(
                            self.app.translate('error-please-reload'),
                            { url: window.location.toString() }
                        )
                    }, true);
                }
            });
        };
        this.addPerson = function(person, event, ui) {
            var operative = new compass.Person(
                self,
                { id: person.id, role: 'developer', effort: 0.0 }
            );
            // TODO: default role should be taken by config
            self.people.push(operative);
            self.save(
                { people: [ operative.toJSON(false) ] },
                {
                    type: 'info',
                    message: base.format(
                        self.app.translate('person-added'),
                        {
                            person: person.name,
                            project: self.name()
                        }
                    )
                });
        };
        this.delPerson = function(person) {
            var i, l, found = -1, people = self.people();
            for(i=0, l=people.length; i<l; i++) {
                if(people[i].id === person.id) {
                    found = i;
                    break;
                }
            }
            if(found > -1) {
                self.people.splice(found, 1);
                self.save(
                    { people: [ person.toJSON(true) ] },
                    {
                        type: 'info',
                        message: base.format(
                            self.app.translate('person-removed'),
                            {
                                person: self.app._people[person.id].name,
                                project: self.name()
                            }
                        )
                    }
                );
            }
        };
    };

    compass.Main = function(roles, people, base_url, plan_weeks,
                            translations) {
        // TODO: make this timeout configurable in Plone
        this.message_timeout = 6;
        this.roles = roles;
        this._people = people;
        this.base_url = base_url;
        this.plan_weeks = ko.observable(plan_weeks);
        this.translations = translations;
        this.people_filter = ko.observable('');
        this.plan_weeks_human = ko.computed(this.getFormattedWeeks, this);
        this.plan_end = ko.computed(this.getPlanEnd, this);
        this.shown_people = ko.computed(this.getShownPeople, this);
        this.roles_list = ko.computed(this.getRolesAsList, this);
        this.active_projects = ko.observableArray([]);
        this.all_projects = ko.observableArray([]);
        this.all_projects_count = null;
        this.all_projects_selected = ko.observable(null);
        this.loaded = ko.observable(false);
        this.transient_messages = ko.observableArray([]);
        this.permanent_messages = ko.observableArray([]);
        this.has_messages = ko.computed(this.hasMessages, this);
        this.active_pane = ko.observable('new');
        this.project_factory = ko.validatedObservable({
            name: ko.observable().extend({ required: true }),
            customer: ko.observable().extend({ required: true }),
            budget: ko.observable().extend({
                required: true,
                pattern: {
                    message: this.translate('invalid-number-value'),
                    params: '^[0-9\.]+$'
                }
            }),
            estimate: ko.observable().extend({
                pattern: {
                    message: this.translate('invalid-number-value'),
                    params: '^[0-9\.]+$'
                }
            })
        });

        var self = this;
        this.reprioritize = function(arg) {
            var i, l, projects_ids = [], projects = arg.sourceParent();
            for(i=0, l=projects.length; i<l; i++)
                projects_ids.push(projects[i].id);
            $.ajax({
                type: 'POST',
                url: self.url('set_priority'),
                data: {
                    projects_ids: projects_ids
                },
                traditional: true,
                dataType: 'json',
                success: function(data, status, request) {
                    self.addMessage({
                        type: 'info',
                        message: self.translate('priority-updated')
                    });
                },
                error: function(request, status, error) {
                    self.addMessage({
                        type: 'error',
                        message: base.format(
                            self.translate('error-please-reload'),
                            { url: window.location.toString() }
                        )
                    }, true);
                }
            });
        };
        this.active_pane.subscribe(function(value) {
            if(value != 'existing')
                self.all_projects_selected(null);
            if(value != 'new') {
                self.project_factory.name();
                self.project_factory.customer();
                self.project_factory.budget();
                self.project_factory.estimate();
            }
        });
    };

    compass.Main.prototype = {
        hasMessages: function() {
            return (this.transient_messages().length > 0 ||
                    this.permanent_messages().length > 0);
        },
        addMessage: function(message, permanent) {
            var self = this;
            if(permanent) {
                this.permanent_messages.push(message);
            }
            else {
                this.transient_messages.push(message);
                window.setTimeout(
                    function() {
                        self.transient_messages.shift();
                    },
                    this.message_timeout * 1000);
            }
        },
        delPerson: function(item, event, ui) {
            item.project.delPerson(item);
        },
        url: function(method) {
            return this.base_url + method;
        },
        translate: function(id) {
            return this.translations[id];
        },
        getRolesAsList: function() {
            var roles_list = [], role_id;
            for(role_id in this.roles) {
                roles_list.push({
                    'value': role_id,
                    'label': this.roles[role_id].name
                });
            }
            return roles_list;
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
            return base.format(
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
        load_all: function() {
            var self = this;
            var start = this.all_projects().length;
            if(this.all_projects_count !== null &&
                    this.all_projects_count <= start)
                return;
            $.ajax({
                dataType: "json",
                url: this.url('get_projects'),
                type: "POST",
                traditional: true,
                data: {
                    start: start
                },
                success: function(data, status, request) {
                    var i, l, project;
                    for(i=0, l=data.length; i<l; i++) {
                        project = data[i];
                        self.all_projects.push(
                            new compass.Project(self, project));
                    }
                }
            });
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
                    self.load_all();
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
            element.find('.addProject').overlay();
            app.load();
            compass.apps.push(app);
            ko.applyBindings(app, this);
        });
    });

})(jQuery);
