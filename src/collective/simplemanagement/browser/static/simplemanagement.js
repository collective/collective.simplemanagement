(function($) {
    if ((typeof window.simplemanagement) === "undefined") {
        window.simplemanagement = {};
    }

    simplemanagement.Planner = function(element) {
        this._init(element);
    };

    simplemanagement.Planner.prototype = {
        _init: function(element) {
            var self = this;
            this.element = $(element);
            this.element_id = this.element.attr('id');
            this.left_selector = $('#'+this.element_id+'-left');
            this.right_selector = $('#'+this.element_id+'-right');
            this.loadStories(this.left_selector);
            this.loadStories(this.right_selector);
            this.left_selector.change(function() {
                self.loadStories(self.left_selector);
            });
            this.right_selector.change(function() {
                self.loadStories(self.right_selector);
            });
        },

        loadStories: function(selector) {
            var self = this;
            var uuid = $('option:selected', selector).val();
            var container = $('#'+selector.attr('id')+'-container');
            container.attr('data-sortable', '');
            container.empty();
            container.load(
                './@@stories',
                {
                    iteration: uuid,
                    widget_id: this.element_id
                },
                function(response, status, request) {
                    self.makeSortable(container);
                }
            );
        },

        makeSortable: function(element) {
            var self = this;
            if(element.attr('data-sortable') === 'true') {
                element.find('ul.sortable').sortable('destroy');
            }
            element.find('ul.sortable').sortable({
                update: function(event, ui) {
                    self.update(event, ui);
                },
                start: function(event, ui) {
                    if(event.ctrlKey || event.metaKey)
                        ui.item.addClass('copy');
                },
                sort: function(event, ui) {
                    if(event.ctrlKey || event.metaKey)
                        ui.item.addClass('copy');
                    else
                        ui.item.removeClass('copy');
                },
                stop: function(event, ui) {
                    ui.item.removeClass('copy');
                },
                receive: function(event, ui) {
                    var destination = $(event.target);
                    var destination_uuid = destination.attr('data-uuid');
                    var origin = $(ui.sender);
                    var origin_uuid = origin.attr('data-uuid');
                    if(origin_uuid === destination_uuid) {
                        $(ui.sender).sortable('cancel');
                    }
                },
                tolerance: 'pointer',
                distance: 5,
                opacity: 0.5,
                revert: true,
                connectWith: '.'+this.element_id+'-stories'
            });
            element.attr('data-sortable', 'true');
        },

        update: function(event, ui) {
            var self = this;
            var destination = $(event.target);
            var destination_uuid = destination.attr('data-uuid');
            var origin = $(ui.sender);
            var origin_uuid = origin.attr('data-uuid');
            var story_id = ui.item.attr('data-storyid');
            if(origin_uuid) {
                if(origin_uuid != destination_uuid) {
                    var origin_url = origin.attr('data-moveurl');
                    //console.log(story_id+': '+origin_uuid+' -> '+destination_uuid+' @ '+ui.item.index());
                    if(origin.children('li').length === 0)
                        origin.siblings('p.discreet').show();
                    var destination_discreet = destination.siblings(
                        'p.discreet');
                    if(destination_discreet.is(':visible'))
                        destination_discreet.hide();
                    var copy = 'false';
                    if(event.ctrlKey || event.metaKey)
                        copy = 'true';
                    $.getJSON(
                        origin_url,
                        {
                            story_id: story_id,
                            new_iteration: destination_uuid,
                            new_position: ui.item.index(),
                            do_copy: copy
                        },
                        function(data) {
                            if(data['success'] === false) {
                                alert(data['error']);
                            }
                            if(copy) {
                                self.loadStories(self.left_selector);
                                self.loadStories(self.right_selector);
                            }
                        }
                    );
                }
            }
            else {
                var destination_url = destination.attr('data-moveurl');
                $.getJSON(
                    destination_url,
                    {
                        story_id: story_id,
                        new_position: ui.item.index()
                    },
                    function(data) {
                        if(data['success'] === false) {
                            alert(data['error']);
                        }
                    }
                );
            }
        }
    };

    simplemanagement.planners = [];

    $(document).ready(function(){

        // taken from kss-bbb.js
        var spinner = $('<div id="ajax-spinner"><img src="' + portal_url + '/spinner.gif" alt=""/></div>');
        spinner.appendTo('body').hide();
        $(document).ajaxStart(function() { spinner.show(); });
        $(document).ajaxStop(function() { spinner.hide(); });

        $('.simplemanagement-planner').each(function() {
            simplemanagement.planners.push(
                new simplemanagement.Planner(this));
        });

        $('#overview ul.tabs').tabs("#overview div.panes > div");


        $('#project-iterations').tabs(
            "#project-iterations div.pane",
            {tabs: 'h2', effect: 'slide', initialIndex: 1}
        );

        $('.quickedit').prepOverlay({
            subtype: 'iframe',
            closeselector: '.button-field',
            config: {
                onClose: function(el){
                    window.location.reload();
                }
            },
            width:'70%'
        });

        $('.quick-booking').prepOverlay({
            subtype: 'ajax',
            filter: common_content_filter,
            formselector: 'form#booking_form',
            config: {
                onClose: function(el){
                    window.location.reload();
                }
            },
            width:'80%'
        });

        $('.story-quickview').prepOverlay({
            subtype: 'ajax',
            filter: common_content_filter,
            width:'80%'
        });

        $('.quickview').prepOverlay({
            subtype: 'ajax',
            // config: {onClose: function(el){
            //     alert('pippo')}
            // },
            filter: common_content_filter,
            width:'50%'
        });


        function updateStoryPosition(event, ui) {
            var position = ui.item.index(),
                item_id = ui.item.attr('id'),
                rows = ui.item.parent().children(),
                iteration_url = ui.item.parents('table').data('iterationurl'),
                row, i;

            $.getJSON(
                iteration_url + '/story_move?story_id=' + item_id + '&new_position=' + position,
                function(data){
                    if(data['success'] === false) {
                        alert(data['error']);
                    }
                    for (i=0; i<rows.length; i++) {
                        row = $(rows[i]);
                        row.removeClass("odd even");
                        if((i%2) === 0) {
                            row.addClass("even");
                        } else {
                            row.addClass("odd");
                        }
                    }

                }
           );
        }

        $( "table.sortable tbody" ).sortable({
            update: updateStoryPosition,
            handle: ".handle",
            tolerance: 'pointer',
            distance: 5,
            opacity: 0.5,
            revert: true
        });

        $('.simple-tooltip[title]').tooltip();

        $('.status').drawer({
            group: '.status',
            position: "top-left",
            css_class: "tooltip",
            offset: [-10, 15],
            content: function(callback, drawer) {
                var handle_span = drawer.trigger.parent().
                    siblings('.handle');
                var url = drawer.trigger.attr('href');
                $.get(url + '/wf_actions', function(data) {
                    var content = $(data);
                    $('a', content).not('.close').bind('click', function(evt){
                        evt.preventDefault();
                        $.getJSON($(this).attr('href'), function(data) {
                            if(data === false) {
                                alert('An error occurred');
                            }
                            else {
                                handle_span.removeClass(
                                    'done in_progress suspended todo');
                                handle_span.addClass(data);
                                drawer.hide();
                            }
                        });
                    });
                    $('a.close', content).click(function(){
                        drawer.hide();
                    });
                    callback(content);
                });
            }
        });

        $('.iteration').drawer({
            group: '.iteration',
            position: "top-left",
            css_class: "tooltip",
            offset: [-10, 15],
            content: function(callback, drawer) {
                var handle_span = drawer.trigger.parent().
                    siblings('.handle');
                var url = drawer.trigger.attr('href');
                $.get(url + '/ch_iteration', function(data) {
                    var content = $(data);
                    $('a', content).not('.close').bind('click', function(evt){
                        evt.preventDefault();
                        $.getJSON($(this).attr('href'), function(data) {
                            if(data === false) {
                                alert('An error occurred');
                            }
                            else {
                                window.location.reload();
                            }
                        });
                    });
                    $('a.close', content).click(function(){
                        drawer.hide();
                    });
                    callback(content);
                });
            }
        });

        var booking_form = $('#booking-tooltip-form').detach();
        $(".bookform").each(function () {
            var trigger = $(this);
            var setupForm = function(form, api) {
                form.attr('action', trigger.attr('rel'));
                form.find('.datepicker').each(function() {
                    var div = $(this);
                    var widget_id = /([a-z\-]+)-picker/.exec(
                        div.attr('id'))[1];
                    div.datepicker({
                        altField: $('#'+widget_id),
                        altFormat: div.attr('data-format'),
                        dateFormat: div.attr('data-format')
                    });
                });
                form.find('input[name="form.buttons.cancel"]').click(
                    function(e) {
                        e.preventDefault();
                        api.hide();
                    }
                );
                var parent = form.parent();
                var options = {
                    success: function (response, status, xhr, form) {
                        response = response.replace(
                                /<script(.|\s)*?\/script>/gi, "");
                        var new_html = $('<div />').append(
                            response).find('form#form');
                        if(new_html.length > 0) {
                            parent.find('form#form').remove();
                            parent.append(new_html);
                            form = parent.find('form#form');
                            setupForm(form, api);
                        }
                        else {
                            api.hide();
                            window.location.reload();
                        }
                    }
                };
                form.ajaxForm(options);
            };
            trigger.drawer({
                group: '.bookform',
                css_class: 'tooltip booking-form',
                position: "left",
                offset: [0, -10],
                content: function(callback, drawer) {
                    var content = $(booking_form.html());
                    var form = content.find('form');
                    setupForm(form, drawer);
                    callback(content);
                }
            });
        });

        $('select.hole-reasons').change(function(){
            $(this).siblings('button').removeAttr('disabled');
        });
        $('.create-hole').click(function(){
            var $self = $(this);
            var date = $(this).attr('data-date');
            var time = $(this).attr('data-time');
            var reason = $(this).siblings('select').val();
            $.getJSON(
                './create-hole?date=' + date +
                             '&time=' + time +
                             '&reason=' + reason,
                function(data){
                    if(data['success']===true) {
                        var $container = $('#missed-bookings');
                        if($container.find('.booking-hole').length==1){
                            $container.animate(
                                { height: 0, opacity: 0 }, 'slow',
                                function() {
                                    $(this).remove();
                                });
                        }else{
                            $self.closest('.booking-hole').animate(
                                { height: 0, opacity: 0 }, 'slow',
                                function() {
                                    $(this).remove();
                                });
                        }
                    }else{
                        alert(data['error']);
                    }
                }
           );
        });

        $('.listing .show-more').drawer({
            group: '.show-more',
            position: "top-left",
            css_class: "tooltip",
            offset: [-10, 15],
            content: function(callback, drawer) {
                var selector = drawer.trigger.data('content');
                callback($(drawer.trigger).siblings(selector).html());
            }
        });

        // ajax submit

        // TODO: prevent unload protection!
        $('#booking_form').ajaxForm({
            /* ajaxify booking form */
            type: 'POST',
            dataType: 'json',
            url: './ajax-create_booking',
            data: $(this).serialize(),
            success: function(result) {
                var $form = $('#booking_form');
                // flush title
                $('#form-widgets-title', $form).val('');
                // flush errors
                $form.siblings('.errors').remove();
                if(result.success && !result.error){
                    // update booking
                    var $target = $('div.booking');
                    if(!$target.length) {
                        $target = $('<div class="booking" />');
                        $(this).after($target);
                    }
                    reload_booking($target);
                    /* XXX 2013-06-13:
                    /  do not reload the form because the calendar widget
                    /  from plone.formwidget.datetime cannot be rebound
                    /  since it has a lot of inline JS */
                    // reload_booking_form($('#booking_form'));
                    // debugger;
                    // clean up fields manually
                    // TODO...
                    return false;
                }else if (result.success && result.error) {
                    // show errors
                    // XXX 2013-06-13: we can do better?
                    var $errwrapper = $('<div class="errors" />');
                    $form.after($errwrapper);
                    var item;
                    $.each(result.errors, function(){
                        item = '<div class="error">';
                        item += '<span class="label">' + this.label + ':</span>';
                        item += '<span class="message">' + this.message + '</span>';
                        item += '</div>';
                        $errwrapper.append(item);
                    });
                    return false;
                }else{
                    alert(data['error']);
                }
            }
        });


        $('.simplemanagement-addstory').each(function() {
            var $container = $(this);
            var $link = $('a', $container);
            var $wrapper = $('.simplemanagement-addstory-form-wrapper', $container);
            var $form = $('form', $container);
            var form_prefix = 'formfield-form-widgets-';
            var $title = $('#' + form_prefix + 'title', $wrapper);
            var $other_fields = $('div[id^="' + form_prefix + '"]').not($title);

            // hide all fields but title on load
            $other_fields.hide();
            $('.formControls', $form).hide();
            $('.created', $wrapper).remove();

            if($('dl.portalMessage', $wrapper).length > 0){
                $wrapper.css('display', 'block');
                add_form_link.addClass('open');
            }

            $title.bind('keyup', function(evt) {
                // $(this).toggleClass('open');
                evt.preventDefault();
                if($other_fields.is(':hidden')) {
                    $other_fields.toggle('slow');
                    $('.formControls', $form).toggle('slow');
                }
            });

            // ajax submit
            $form.ajaxForm({
                type: 'POST',
                dataType: 'json',
                url: './add-story',
                data: $form.serialize(),
                success: function(resp) {
                    if(resp.success && !resp.error){
                        // TODO reload story listing
                        // empty fields
                        $(':input', $title).val('');
                        $other_fields.each(function(){
                            // $(this).toggle('slow');
                            $(':input', $(this)).val('');
                        });
                        // remove token input elements
                        $('.token-input-token-facebook', $form).remove();

                        // $('.formControls', $form).toggle('slow');
                        if(resp.result && resp.result.created) {
                            var $created = $('<div class="created" />');
                            $created.append('<span class="label">' + resp.result.created.msg + '</span>');
                            var url = '<a class="created-url"'; 
                            url += 'href="' + resp.result.created.url  +'">';
                            url += resp.result.created.title + '</a>';
                            $created.append(url);
                            $created.hide();
                            $form.before($created);
                            $created.toggle('slow');
                        }
                        return false;
                    }else if (resp.success && resp.error) {
                        // XXX 2013-06-13: we can do better?
                        var $errwrapper = $('<div class="errors" />');
                        $form.after($errwrapper);
                        var item;
                        $.each(resp.errors, function(){
                            item = '<div class="error">';
                            item += '<span class="label">' + this.label + ':</span>';
                            item += '<span class="message">' + this.message + '</span>';
                            item += '</div>';
                            $errwrapper.append(item);
                        });
                        return false;
                    }else{
                        alert(data['error']);
                    }
                }
            });
        });

    });
})(jQuery);


function reload_booking(sel) {
    $.getJSON(
        './reload-booking',
        function(data){
            if(data['success']===true) {
                $(sel).html(data['bookings_html']);
                $('table.timing').html(data['timing_html']);
            }else{
                alert(data['error']);
            }
        }
    );
}

function reload_stories(sel) {
    $.getJSON(
        './reload-stories',
        function(data){
            if(data['success']===true) {
                $(sel).html(data['stories_html']);
            }else{
                alert(data['error']);
            }
        }
    );
}


function get_booking_form(){
    $.getJSON(
        './reload-booking-form',
        function(data){
            if(data['success']===true) {
                return data['html'];
            }else{
                return false;
            }
        }
    );
}

function reload_booking_form(sel) {
    var content = get_booking_form();
    if (content) {
        $(sel).html(content).html();
    }
}