/*global window, jQuery, document, alert,
  portal_url, common_content_filter */
(function ($) {
    "use strict";

    if (window.simplemanagement === undefined) {
        window.simplemanagement = {};
    }

    var sm = window.simplemanagement;

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

        $('.sm-booking-form-link').prepOverlay({
            subtype: 'ajax',
            filter: common_content_filter,
            formselector: 'form#booking_form',
            width: '80%',
            height: '90%',
            config: {
                onClose: function(el) {
                    value.model.load();
                },
                onBeforeLoad: function() {
                    var $overlay = this.getOverlay();
                    $overlay.height($(window).height() * 0.8);
                    $overlay.find('.pb-ajax').css('height', '100%');
                },
                onLoad: function() {
                    sm.init_widgets();
                }
            }
        });

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

        var init_dash_bk_form = function() {
            $('.template-dashboard #booking_form').ajaxForm({
                target: '#booking-form',
                success: function() {
                    init_dash_bk_form();
                    sm.init_widgets();
                }
            });
        };
        init_dash_bk_form();

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
