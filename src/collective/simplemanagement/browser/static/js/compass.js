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
        this.name = ko.computed(this.getName, this);

        // TODO: in this file we are using a mix & match of approaches,
        // we should standardize
        var self = this;
        this.workloads = function() {
            var effort = 0;
            var people_effort = self.project.app.people_effort();
            var working_total_days = self.project.app.working_total_days();
            if(people_effort[self.id])
                effort = people_effort[self.id];
            return {
                effort: effort,
                total: working_total_days,
                minimum: working_total_days *
                    (1.0 - self.project.app.warning_delta)
            };
        };
        this.is_critical = ko.computed(function() {
            var load = self.workloads();
            return (load.effort > load.total);
        });
        this.is_free = ko.computed(function() {
            var load = self.workloads();
            return (load.effort <= load.minimum);
        });
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
            return this.project.id().replace(/\//g, '-') + '-' +
                    this.id.replace('.', '-');
        },
        getAvatar: function() {
            var data = this.project.app._people[this.id];
            if(data){
                return data.avatar;
            }
            return '';
        },
        getName: function() {
            var data = this.project.app._people[this.id];
            if(data){
                return data.name;
            }
            return '';
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
        this.url = ko.observable(data.url);
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
        this.people_effort = ko.computed(function() {
            var i, l, person, people = self.people(), effort = {};
            for(i=0, l=people.length; i<l; i++) {
                person = people[i];
                if(effort[person.id] === undefined)
                    effort[person.id] = parseFloat(person.effort(), 10);
                else
                    effort[person.id] += person.effort();
            }
            return effort;
        });
        this.hidden = ko.computed(function() {
            var i, l;
            var selected_person = self.app.selected_person();
            if(selected_person === null) return false;
            var people = self.people();
            for(i=0, l=people.length; i<l; i++) {
                if(selected_person == people[i].id)
                    return false;
            }
            return true;
        });
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
                    simplemanagement.messages.addMessage(message);
                },
                error: function(request, status, error) {
                    simplemanagement.messages.addMessage({
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
            var i, l, all_people = self.people();
            for(i=0, l=all_people.length; i<l; i++) {
                if(person.id === all_people[i].id)
                    return false;
            }
            // TODO: default role should be taken by config
            var operative = new compass.Person(
                self,
                { id: person.id, role: 'developer', effort: 0.0 }
            );
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
            return true;
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
        this.deactivate = function() {
            self.app.deactivateProject(self);
        };
    };

    compass.Project.prototype = {
        toJSON: function() {
            var i, l, people, data = {
                id: this.id(),
                url: this.url(),
                name: this.name(),
                status: this.status(),
                customer: this.customer(),
                effort: this.effort(),
                notes: this.notes(),
                css_class: this.css_class(),
                people: []
            };
            people = this.people();
            for(i=0, l=people.length; i<l; i++) {
                data.people.push({
                    id: people[i].id,
                    effort: people[i].effort(),
                    role: people[i].display_role(),
                    is_critical: people[i].is_critical(),
                    is_free: people[i].is_free()
                });
            }
            return data;
        },
        validate: function() {
            var i, l, people, total_effort, person_effort;
            total_effort = 0;
            people = this.people();
            for(i=0, l=people.length; i<l; i++) {
                person_effort = people[i].effort();
                if(person_effort === 0) return false;
                total_effort += people[i].effort();
            }
            if(total_effort > this.effort()) return false;
            return true;
        }
    };

    compass.Main = function(roles, people, base_url, plan_weeks,
                            working_week_days, warning_delta, last_snapshot,
                            translations) {
        // TODO: make this timeout configurable in Plone
        this.overlay = null;
        this.roles = roles;
        this._people = people;
        this.base_url = base_url;
        this.working_week_days = working_week_days;
        this.warning_delta = warning_delta;
        this.plan_weeks = ko.observable(plan_weeks);
        this.translations = translations;
        this.people_filter = ko.observable('');
        this.selected_person = ko.observable(null);
        this.plan_weeks_human = ko.computed(this.getFormattedWeeks, this);
        this.plan_end = ko.computed(this.getPlanEnd, this);
        this.roles_list = ko.computed(this.getRolesAsList, this);
        this.active_projects = ko.observableArray([]);
        this.all_projects = ko.observableArray([]);
        this.all_projects_count = null;
        this.all_projects_query = ko.throttledObservable(null, 1500);
        this.loaded = ko.observable(false);
        this.last_snapshot = ko.observable(last_snapshot);
        this.active_pane = ko.observable('new');
        this.project_factory_validate = ko.observable(true);
        this.project_factory = ko.validatedObservable({
            name: ko.observable().extend({
                required: {
                    message: this.translate('invalid-required'),
                    params: true
                }
            }),
            customer: ko.observable().extend({
                required: {
                    message: this.translate('invalid-required'),
                    params: true
                }
            }),
            budget: ko.observable().extend({
                required: {
                    message: this.translate('invalid-required'),
                    params: true
                },
                number: {
                    message: this.translate('invalid-number-value'),
                    params: true
                }
            }),
            estimate: ko.observable().extend({
                number: {
                    message: this.translate('invalid-number-value'),
                    params: true
                }
            })
        });

        var self = this;
        this.working_total_days = ko.computed(function() {
            return self.working_week_days * self.plan_weeks();
        });
        this.people_effort = ko.computed(function() {
            var i, l, project, project_effort, person_id,
                projects = self.active_projects(), effort = {};
            for(i=0, l=projects.length; i<l; i++) {
                project = projects[i];
                project_effort = project.people_effort();
                for(person_id in project_effort) {
                    if(effort[person_id] === undefined)
                        effort[person_id] = project_effort[person_id];
                    else
                        effort[person_id] += project_effort[person_id];
                }
            }
            return effort;
        });
        this.shown_people = ko.computed(this.getShownPeople, this);
        this.total_effort = ko.computed(function() {
            var result = 0, person_id, people_effort = self.people_effort();
            for(person_id in people_effort) {
                result += people_effort[person_id];
            }
            return result;
        });
        this.critical_resources = ko.computed(function() {
            var person_id, data, people_effort = self.people_effort(),
                critical = [];
            for(person_id in people_effort) {
                if(people_effort[person_id] > self.working_total_days()) {
                    data = {
                        id: person_id,
                        name: person_id,
                        effort: people_effort[person_id],
                        avatar: ''
                    };
                    if(self._people[person_id]) {
                        data.name = self._people[person_id].name;
                        data.avatar = self._people[person_id].avatar;
                    }
                    critical.push(data);
                }
            }
            return critical;
        });
        this.reprioritize = function() {
            var i, l, projects_ids = [], projects = self.active_projects();
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
                    simplemanagement.messages.addMessage({
                        type: 'info',
                        message: self.translate('priority-updated')
                    });
                    var i, l, project;
                    for(i=0, l=projects.length; i<l; i++) {
                        project=projects[i];
                        project.priority(data[project.id]);
                    }
                },
                error: function(request, status, error) {
                    simplemanagement.messages.addMessage({
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
                self.all_projects_query(null);
            if(value != 'new') {
                self.resetFactory();
            }
        });
        this.all_projects_query.subscribe(function() {
            self.load_all(true);
        });
        this.load_more = function() {
            self.load_all();
        };
        this.snapshot = function() {
            var i, l, active_projects, critical_resources, data;
            data = {
                projects: [],
                total: self.total_effort(),
                critical: [],
                plan_end: self.plan_end()
            };
            active_projects = self.active_projects();
            for(i=0, l=active_projects.length; i<l; i++) {
                if(!active_projects[i].validate()) {
                    simplemanagement.messages.addMessage({
                        type: 'warning',
                        message: base.format(
                            self.translate('project-invalid'),
                            { project: active_projects[i].name() }
                        )
                    }, true);
                    return false;
                }
                data.projects.push(active_projects[i].toJSON());
            }
            critical_resources = self.critical_resources();
            for(i=0, l=critical_resources.length; i<l; i++) {
                data.critical.push({
                    id: critical_resources[i].id,
                    effort: critical_resources[i].effort
                });
            }
            $.ajax({
                type: 'POST',
                url: self.url('take_snapshot'),
                data: {
                    data: JSON.stringify(data)
                },
                traditional: true,
                dataType: 'json',
                success: function(data, status, request) {
                    simplemanagement.messages.addMessage({
                        type: 'info',
                        message: self.translate('snapshot-taken')
                    });
                    self.last_snapshot(data.url);
                },
                error: function(request, status, error) {
                    simplemanagement.messages.addMessage({
                        type: 'error',
                        message: base.format(
                            self.translate('error-please-reload'),
                            { url: window.location.toString() }
                        )
                    }, true);
                }
            });
            return true;
        };
    };

    compass.Main.prototype = {
        choosePerson: function(person_id) {
            var chosen = this.selected_person();
            if(chosen !== person_id)
                this.selected_person(person_id);
            else
                this.selected_person(null);
        },
        resetFactory: function() {
            var factory = this.project_factory();
            factory.name(undefined);
            factory.customer(undefined);
            factory.budget(undefined);
            factory.estimate(undefined);
            factory.errors.showAllMessages(false);
        },
        createProject: function() {
            var factory, data, self = this;
            if(!this.project_factory.isValid()) {
                this.project_factory.errors.showAllMessages();
                return false;
            }
            factory = this.project_factory();
            data = {
                name: factory.name(),
                customer: factory.customer(),
                budget: factory.budget(),
                estimate: factory.estimate()
            };
            $.ajax({
                type: 'POST',
                url: this.url('create_project'),
                data: {
                    data: JSON.stringify(data),
                    priority: this.active_projects().length
                },
                traditional: true,
                dataType: 'json',
                success: function(data, status, request) {
                    simplemanagement.messages.addMessage({
                        type: 'info',
                        message: base.format(
                            self.translate('project-created'),
                            { project: data.name }
                        )
                    });
                    self.active_projects.push(
                        new compass.Project(self, data));
                },
                error: function(request, status, error) {
                    simplemanagement.messages.addMessage({
                        type: 'error',
                        message: base.format(
                            self.translate('error-please-reload'),
                            { url: window.location.toString() }
                        )
                    }, true);
                }
            });
            if(this.overlay && this.overlay.isOpened())
                this.overlay.close();
            this.resetFactory();
            return true;
        },
        activateProject: function(project) {
            var self = this;
            this.active_projects.push(project);
            project.priority(this.active_projects().length);
            project.active(true);
            project.save(
                { active: project.active(),
                  priority: project.priority() },
                {
                    type: 'info',
                    message: base.format(
                        self.translate('project-activated'),
                        { project: project.name() }
                    )
                }
            );
            if(this.overlay && this.overlay.isOpened())
                this.overlay.close();
        },
        deactivateProject: function(project) {
            var i, l, index = null, self = this,
                active_projects = this.active_projects();
            for(i=0, l=active_projects.length; i<l; i++) {
                if(project.id == active_projects[i].id) {
                    index = i;
                    break;
                }
            }
            if(index !== null) {
                project = this.active_projects.splice(index, 1)[0];
                project.active(false);
                project.save(
                    { active: project.active() },
                    {
                        type: 'info',
                        message: base.format(
                            self.translate('project-deactivated'),
                            { project: project.name() }
                        )
                    }
                );
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
            return $.datepicker.formatDate('d MM yy', end);
        },
        getFormattedWeeks: function() {
            var weeks = this.plan_weeks();
            return base.format(
                this.translate(weeks > 1 ? 'weeks' : 'week'),
                { 'week': weeks }
            );
        },
        getShownPeople: function() {
            var f_id, f_name, effort, is_critical, is_free, not_chosen;
            var people = [];
            var people_effort = this.people_effort();
            var filter = this.people_filter().toLowerCase();
            var working_total_days = this.working_total_days();
            var selected_person = this.selected_person();
            for(var id in this._people) {
                f_id = id.toLowerCase();
                f_name = this._people[id]['name'].toLowerCase();
                if(filter === '' ||
                        f_id.indexOf(filter) !== -1 ||
                        f_name.indexOf(filter) !== -1) {
                    not_chosen = false;
                    effort = 0;
                    is_critical = false;
                    if(people_effort[id]) {
                        effort = people_effort[id];
                        if(people_effort[id] > working_total_days)
                            is_critical = true;
                    }
                    is_free = effort <= (working_total_days *
                                         (1.0 - this.warning_delta));
                    if(selected_person !== null && selected_person !== id)
                        not_chosen = true;
                    people.push({
                        'id': id,
                        'name': this._people[id]['name'],
                        'avatar': this._people[id]['avatar'],
                        'effort': effort,
                        'is_critical': is_critical,
                        'is_free': is_free,
                        'not_chosen': not_chosen
                    });
                }
            }
            return people;
        },
        load_all: function(reset) {
            var start, query, self = this;
            if(reset) {
                this.all_projects_count = null;
                this.all_projects([]);
            }
            else {
                start = this.all_projects().length;
            }
            if(this.all_projects_count !== null &&
                    this.all_projects_count <= start)
                return false;
            query = this.all_projects_query();
            $.ajax({
                dataType: "json",
                url: this.url('get_all_projects'),
                type: "POST",
                traditional: true,
                data: {
                    start: start,
                    query: query ? query : ''
                },
                success: function(data, status, request) {
                    var i, l, project, items=data.items;
                    for(i=0, l=items.length; i<l; i++) {
                        project = items[i];
                        self.all_projects.push(
                            new compass.Project(self, project));
                    }
                    self.all_projects_count = data.count;
                }
            });
            return true;
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

    compass.History = function(list_keys_url) {
        this.list_keys_url = list_keys_url;
        this.keys = ko.observableArray([]);
        this.keys_count = null;
        this.loading = false;

        var self = this;
        // TODO: this infinite scroller might have bugs,
        // we should chain calls like we do in eprice
        this.load = function() {
            if(self.loading) return false;
            self.loading = true;
            var start, query;
            start = self.keys().length;
            if(self.keys_count !== null && self.keys_count <= start)
                return false;
            $.ajax({
                dataType: "json",
                url: self.list_keys_url,
                type: "POST",
                traditional: true,
                data: {
                    start: start
                },
                success: function(data, status, request) {
                    var i, l, keys=data.items;
                    for(i=0, l=keys.length; i<l; i++) {
                        console.log(keys[i]);
                        self.keys.push({
                            title: $.datepicker.formatDate(
                                'd MM yy', new Date(keys[i].value*1000)),
                            url: keys[i].url,
                            active: (
                                keys[i].url.replace(/\/$/, '') ==
                                    window.location.toString().
                                        replace(/\/$/, ''))
                        });
                    }
                    self.keys_count = data.count;
                    self.loading = false;
                }
            });
            return true;
        };
        this.load();
    };

    compass.apps = [];

    $(document).ready(function() {
        ko.validation.init();
        $('.compassview.editmode').each(function() {
            var element = $(this);
            var app = new compass.Main(
                $.parseJSON(element.attr('data-roles')),
                $.parseJSON(element.attr('data-people')),
                element.attr('data-base-url'),
                $.parseJSON(element.attr('data-plan-weeks')),
                $.parseJSON(element.attr('data-working-week-days')),
                $.parseJSON(element.attr('data-warning-delta')),
                element.attr('data-last-snapshot'),
                $.parseJSON(element.attr('data-translations')));
            element.find('.addProject').overlay({
                onBeforeLoad: function(e) {
                    app.load_all(true);
                }
            });
            app.overlay = element.find('.addProject').data('overlay');
            app.load();
            compass.apps.push(app);
            ko.applyBindings(app, this);
            $('#peopleToolbox').fixedbox();
        });
        $('.compassview.historymode').each(function() {
            var element = $(this);
            var app = new compass.History(
                element.attr('data-list-keys-url'));
            element.find('.delete').overlay();
            app.load();
            compass.apps.push(app);
            ko.applyBindings(app, this);
        });
    });

})(jQuery);
