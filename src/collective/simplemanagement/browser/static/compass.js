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
        this.addPerson = function(person, event, ui) {
            // TODO: default role should be taken by config
            self.people.push(new compass.Person(
                self,
                { id: person.id, role: 'developer', effort: 0.0 }
            ));
            self.app.addMessage({
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
            if(found > -1) self.people.splice(found, 1);
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
        this.messages = ko.observableArray([]);
    };

    compass.Main.prototype = {
        addMessage: function(message) {
            var self = this;
            this.messages.push(message);
            window.setTimeout(
                function() {
                    self.messages.pop();
                },
                this.message_timeout * 1000);
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
