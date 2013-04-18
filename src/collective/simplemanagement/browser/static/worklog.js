(function($) {
    if ((typeof window.simplemanagement) === "undefined") {
        window.simplemanagement = {};
    }
    var sm = window.simplemanagement;
    if ((typeof sm.worklog) === "undefined") {
        sm.worklog = {};
    }
    var worklog = sm.worklog;

    worklog.Worklog = function(element) {
        this.root = $(element);
        this.form = this.root.find('form.resources');
        this.resources = $.parseJSON(this.root.attr('data-resources'));
        this.current = null;
        this.backend = {
            url: this.form.attr('action'),
            method: this.form.attr('method').toUpperCase()
        };
        this.calendar_table = this.root.find('.calendar table');
        this.row_template = this.calendar_table.find('tbody tr').detach();
        this.details_template = this.root.find('.booking-details').detach();
        this.initial_load = true;
        this.controls = {
            previous: this.root.find('.calendar .previous'),
            next: this.root.find('.calendar .next')
        };
        this.bind();
        this.load();
    };

    worklog.Worklog.prototype = {
        bind: function() {
            var self = this;
            var resources = this.root.find(
                'form.resources input[type="checkbox"]');
            resources.change(function() {
                self.load(self.current);
            });
        },
        render: function(title, hours) {
            var self = this;
            var tbody = this.calendar_table.find('tbody');
            this.root.find('.calendar h2 span').html(title);
            tbody.empty();
            for(var i=0; i<hours.length; i++) {
                var identifier = hours[i][0];
                var resources = hours[i][1];
                row = this.row_template.clone();
                row.appendTo(tbody);
                row.find('.week-info').html(identifier);
                if (resources.length > 0) {
                    row.find('.week-info').attr('rowspan', resources.length);
                }
                row.addClass('week-start');
                for(var j=0; j<resources.length; j++) {
                    var res_row = row;
                    var resource = this.resources[resources[j][0]];
                    var week_hours = resources[j][1];
                    res_row.find('.resource-info img').attr(
                            'title', resource.fullname);
                    res_row.find('.resource-info span').text(resource.fullname);
                    if(resource.portrait) {
                        res_row.find('.resource-info img').attr(
                            'src',
                            resource.portrait);
                    }
                    res_row.find('td.date-column').each(function(k) {
                        var total = week_hours[k].total,
                            link = $('a', this);
                        link.
                            attr(
                                'data-details-url',
                                week_hours[k].href).
                            text(
                                week_hours[k].total).
                            addClass(
                                week_hours[k]['class']);
                        if (total == '0.00') {
                            link.hide();
                        }
                        else {
                            link.show();
                        }
                    });
                    if((j%2) === 0) {
                        res_row.removeClass('odd');
                        res_row.addClass('even');
                    }
                    if(j < (resources.length-1)) {
                        row = this.row_template.clone();
                        row.appendTo(tbody);
                        row.find('.week-info').remove();
                    }
                }
            }
            if(this.initial_load) {
                this.root.children().each(function() {
                    $(this).animate({ opacity: 1 });
                });
                this.initial_load = false;
            }
        },
        bind_details: function() {
            var self = this;
            var tbody = this.calendar_table.find('tbody');
            tbody.find('td.date-column a[title]').each(function(i) {
                $(this).drawer({
                    group: tbody.find('td.date-column a[title]'),
                    position: 'bottom-left',
                    css_class: 'tooltip',
                    offset: [ 7, 20 ],
                    content: function(callback, drawer) {
                        var trigger = drawer.trigger;
                        $.get(
                            trigger.attr('data-details-url'),
                            {},
                            function(data) {
                                var row,
                                    content = self.details_template.clone();
                                var tbody = content.find('table tbody');
                                var row_template = tbody.find('tr').detach();
                                if(data.length === 0) {
                                    row = row_template.clone();
                                    row.find('td:eq(0)').attr(
                                        'colspan', '4');
                                    row.find('td:eq(1)').remove();
                                    row.find('td:eq(1)').remove();
                                    tbody.append(row);
                                }
                                for(var i=0; i<data.length; i++) {
                                    row = row_template.clone();
                                    row.find('td:eq(0)').empty();
                                    switch(data[i].type) {
                                    case "hole": {
                                        row.find('td:eq(0)').text(
                                            data[i].reason);
                                        row.find('td:eq(0)').attr(
                                            'colspan', '3');
                                        row.find('td:eq(3)').text(
                                            data[i].hours);
                                        row.find('td:eq(1)').remove();
                                        row.find('td:eq(1)').remove();
                                        break;
                                    }
                                    case "booking": {
                                        row.find('td:eq(0)').text(
                                            data[i].project);
                                        row.find('td:eq(1)').text(
                                            data[i].story);
                                        row.find('td:eq(2)').text(
                                            data[i].booking);
                                        row.find('td:eq(3)').text(
                                            data[i].hours);
                                        break;
                                    }
                                    default:
                                        break;
                                    }
                                    tbody.append(row);
                                }
                                callback(content);
                            },
                            "json");
                    }
                });
            });
        },
        load: function(month) {
            var self = this;
            var data = {
                resources: []
            };
            this.form.find('input[name="resources"]:checked').each(function() {
                data.resources.push($(this).val());
            });
            if((typeof month) != "undefined" && month !== null)
                data.month = month;
            $.ajax({
                url: this.backend.url,
                data: data,
                dataType: "json",
                type: this.backend.method,
                traditional: true,
                success: function(data, status, request) {
                    self.current = data.current.value;
                    self.controls.previous.attr(
                        'title', data.previous.title);
                    self.controls.next.attr(
                        'title', data.next.title);
                    self.render(data.current.title, data.total_hours);
                    self.controls.previous.unbind('click');
                    self.controls.previous.click(function(e) {
                        e.preventDefault();
                        self.load(data.previous.value);
                    });
                    self.controls.next.unbind('click');
                    self.controls.next.click(function(e) {
                        e.preventDefault();
                        self.load(data.next.value);
                    });
                    self.bind_details();
                }
            });
        }
    };

    worklog._worklog = null;

    worklog.make = function(id) {
        worklog._worklog = new worklog.Worklog($('#'+id));
    };
})(jQuery);
