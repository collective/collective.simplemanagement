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
                    // $(sel).html(data.bookings_html);
                    // $('table.timing').html(data.timing_html);
                    window.location.reload();
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
