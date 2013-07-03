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

    ko.bindingHandlers.jqueryDrawer = {
        init: function(element, accessor) {
            var value = accessor();
            var content = $(value.content).removeAttr('style').detach();
            $(element).drawer({
                group: value.group ? value.group : null,
                content: function(callback) {
                    callback(content);
                },
                position: value.position ? value.position : "bottom",
                css_class: value.css_class ? value.css_class : "tooltip",
                remove: false
            });
        }
    };

    // http://stackoverflow.com/a/15812995/967274
    // The responder is the creator of knockout-sortable.
    ko.bindingHandlers.droppable = {
        init: function(element, valueAccessor) {
            var value = valueAccessor() || {};
            var action = value.action || value;

            var options = {
                drop: function(event, ui) {
                    var item = ko.utils.domData.get(
                        ui.draggable[0],
                        "ko_dragItem");

                    if (item) {
                        item = item.clone ? item.clone() : item;
                        action.call(this, item, event, ui);
                    }
                }
            };
            $.extend(options, value.options || {});

            $(element).droppable(options);
        }
    };

    compass.Person = function(project, data) {
        this.project = project;
        this.id = data.id;
        this.role = ko.observable(data.role);
        this.effort = ko.observable(data.effort);
        this.dom_id = ko.computed(this.domId, this);
        this.display_role = ko.computed(this.getDisplayRole, this);
        this.avatar = ko.computed(this.getAvatar, this);
        var self = this;
        this.role.subscribe(function(value) {
            self.project.save(
                { people: [ self.toJSON() ] },
                {
                    type: 'info',
                    message: compass.format(
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
                    message: compass.format(
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
                    message: compass.format(
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
                        message: compass.format(
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
                    message: compass.format(
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
                        message: compass.format(
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
        this.loaded = ko.observable(false);
        this.transient_messages = ko.observableArray([]);
        this.permanent_messages = ko.observableArray([]);
        this.has_messages = ko.computed(this.hasMessages, this);

        var self = this;
        
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
