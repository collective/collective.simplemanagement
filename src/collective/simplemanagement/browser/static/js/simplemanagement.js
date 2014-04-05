/*global window, jQuery, document, alert,
  portal_url, common_content_filter */
(function ($) {
    "use strict";

    if (window.simplemanagement === undefined) {
        window.simplemanagement = {};
    }

    var sm = window.simplemanagement;

    sm.reload_booking = function (sel) {
        $.getJSON(
            './reload-booking',
            function(data) {
                if (data.success === true) {
                    $(sel).html(data.bookings_html);
                    $('table.timing').html(data.timing_html);
                } else {
                    alert(data.error);
                }
            }
        );
    };

    sm.booking_tooltip = function() {
        $('.listing .show-more').drawer({
            group: '.show-more',
            position: "top-center",
            css_class: "tooltip",
            offset: [-10, 15],
            content: function(callback, drawer) {
                var selector = drawer.trigger.data('content'),
                    content = $(drawer.trigger).siblings(selector).clone();
                $('a.close', content).bind('click', function (evt) {
                    drawer.hide();
                    evt.preventDefault();
                });
                callback(content);
            }
        });
    };

    /* init widget for popup forms */
    sm.init_widgets = function() {
        sm.booking_tooltip();
        $('.select2-multi-widget').select2Widget({multiple: true});
        $('.select2-widget').select2Widget();
        $('.book-widget').bookWidget();
    };

    $(document).ready(function() {

        // select2 init
        $("select#language").select2();
        $(".select-widget.choice-field").select2();

        // init knockout iteration view
        $('.iteration-stories').iterationView();
        $('.project-iterations').projectView();


        // init planner javascript
        $('.simplemanagement-planner').each(function() {
            sm.planners.push(
                new sm.Planner(this)
            );
        });

        // generic tooltip that displays the title of an element
        $('.simple-tooltip[title]').tooltip();

        // initialize booking tooltip in story view
        sm.booking_tooltip();


        // initialize tabs in project view
        $('.portaltype-project #overview ul.tabs').tabs(
            "#overview div.panes > div",
            {
                history: false // i don't like how it works :(
            }
        );

        // initialize tabs in dashboard
        $('.template-dashboard #overview ul.tabs').tabs(
            "#overview div.panes > div"
        );

        // initialize tabs in report view
        $('.template-report #overview ul.tabs').tabs(
            "#overview div.panes > div"
        );


        // Show and hide add story form on press key in 'title' input
        $('#addstory-form').each(function () {
            var self = $(this),
                form_prefix = 'formfield-form-widgets-',
                title = $('#' + form_prefix + 'title', self),
                other_fields = $('div[id^="' + form_prefix + '"]', self).not(title),
                form_controls = $('.formControls', self);
            other_fields.hide();
            form_controls.hide();

            title.bind('keyup', function(evt) {
                // $(this).toggleClass('open');
                evt.preventDefault();
                if (other_fields.is(':hidden')) {
                    other_fields.toggle('slow');
                    form_controls.toggle('slow');
                }
            });
        });

        // Booking form in dashboard
        sm.booking_form = $('#booking-tooltip-form').detach();
        $(".bookform").each(function () {
            var trigger = $(this),
                setupForm;
            setupForm = function(form, api) {
                form.attr('action', trigger.attr('rel'));
                form.find('.datepicker').each(function() {
                    var div = $(this);
                    var widget_id = /([a-z\-]+)-picker/.exec(
                        div.attr('id')
                    )[1];
                    div.datepicker({
                        altField: '#' + widget_id,
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
                        response = response.replace(/<script(.|\s)*?\/script>/gi, "");
                        var new_html = $('<div />').append(
                            response
                        ).find('form#form');
                        if (new_html.length > 0) {
                            parent.find('form#form').remove();
                            parent.append(new_html);
                            form = parent.find('form#form');
                            setupForm(form, api);
                        } else {
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
                    var content = $(sm.booking_form.html()),
                        form = content.find('form');
                    setupForm(form, drawer);
                    callback(content);
                }
            });
        });

        // manage booking holes init
        $('select.hole-reasons').change(function() {
            $(this).siblings('button').removeAttr('disabled');
        });
        $('.create-hole').click(function() {
            var $self = $(this),
                date = $(this).attr('data-date'),
                time = $(this).attr('data-time'),
                reason = $(this).siblings('select').val();
            $.getJSON(
                './create-hole?date=' + date + '&time=' + time + '&reason=' + reason,
                function(data) {
                    if (data.success === true) {
                        var $container = $('#missed-bookings');
                        if ($container.find('.booking-hole').length === 1) {
                            $container.animate(
                                {height: 0, opacity: 0},
                                'slow',
                                function() {
                                    $(this).remove();
                                }
                            );
                        } else {
                            $self.closest('.booking-hole').animate(
                                {height: 0, opacity: 0},
                                'slow',
                                function() {
                                    $(this).remove();
                                }
                            );
                        }
                    } else {
                        alert(data.error);
                    }
                }
            );
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
                var $form = $('#booking_form'),
                    to_exit = true,
                    $target,
                    $errwrapper,
                    item;
                // flush errors
                $form.siblings('.errors').remove();
                if (result.success && !result.error) {
                    // update booking
                    $target = $('div.booking');
                    if (!$target.length) {
                        $target = $('<div class="booking" />');
                        $(this).after($target);
                    }
                    sm.reload_booking($target);
                    /* XXX 2013-06-13:
                    /  do not reload the form because the calendar widget
                    /  from plone.formwidget.datetime cannot be rebound
                    /  since it has a lot of inline JS */
                    // reload_booking_form($('#booking_form'));
                    // debugger;
                    to_exit = false;
                } else if (result.success && result.error) {
                    // show errors
                    // XXX 2013-06-13: we can do better?
                    $errwrapper = $('<div class="errors" />');
                    $form.after($errwrapper);
                    $.each(result.errors, function() {
                        item = '<div class="error">';
                        item += '<span class="label">' + this.label + ':</span>';
                        item += '<span class="message">' + this.message + '</span>';
                        item += '</div>';
                        $errwrapper.append(item);
                    });
                    to_exit = false;
                } else {
                    alert(result.error);
                }
                return to_exit;
            }
        });


        // Show animated spinner while AJAX is loading.
        // See: kss-bbb.js
        if ($('#ajax-spinner').length === 0) {
            var spinner = $('<div id="ajax-spinner"><img src="' + portal_url + '/spinner.gif" alt=""/></div>');
            spinner.appendTo('body').hide();
            $(document).ajaxStart(function() { spinner.show(); });
            $(document).ajaxStop(function() { spinner.hide(); });
        }

    });

}(jQuery));
