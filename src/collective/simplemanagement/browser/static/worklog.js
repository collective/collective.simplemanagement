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
        this.resources = $.loadJSON(this.root.attr('data-resources'));
        this.current = null;
        this.backend = {
            url: this.form.attr('action'),
            method: this.form.attr('method').toUpper()
        };
        this.row_template = this.root.find('table tbody tr').detach();
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
            var tbody = this.root.find('.calendar table tbody');
            this.root.find('.calendar h2 span').html(title);
            tbody.empty();
            for(var i=0; i<hours.length; i++) {
                var identifier = hours[i][0];
                var resources = hours[i][1];
                row = this.row_template.clone();
                row.appendTo(tbody);
                row.find('.week-info').text(identifier);
                row.find('.week-info').attr('rowspan', resources.length);
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
                        $('a', this).attr('href', week_hours[k].href).text(
                            week_hours[k].total).addClass(
                                week_hours[k]['class']);
                    });
                    if(j<(hours.length-1)) {
                        res_row = this.row_template.clone();
                        res_row.appendTo(tbody);
                        res_row.find('.week-info').remove();
                    }
                }
            }
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
            $.ajax(
                this.backend.url,
                {
                    data: data,
                    dataType: "json",
                    type: this.backend.method,
                    success: function(data, status, request) {
                        self.current = data.current.value;
                        self.root.find('.calendar .previous').attr(
                            'title', data.previous.title);
                        self.root.find('.calendar .previous').click(function(e) {
                            e.preventDefault();
                            self.load(data.previous.value);
                        });
                        self.root.find('.calendar .next').attr(
                            'title', data.next.title);
                        self.root.find('.calendar .next').click(function(e) {
                            e.preventDefault();
                            self.load(data.next.value);
                        });
                        self.render(data.current.title, data.total_hours);
                    }
                }
            );
        }
    };
})(jQuery);
