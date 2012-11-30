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
            this.has_sortable = false;
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
            container.load(
                './@@stories',
                {
                    iteration: uuid,
                    widget_id: this.element_id
                },
                function(response, status, request) {
                    self.makeSortable();
                }
            );
        },

        makeSortable: function() {
            var self = this;
            if(this.has_sortable) {
                $('ul.sortable', this.element).sortable('destroy');
                this.has_sortable = false;
            }
            $('ul.sortable', this.element).sortable({
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
            this.has_sortable = true;
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

        $('.simplemanagement-planner').each(function() {
            simplemanagement.planners.push(
                new simplemanagement.Planner(this));
        });

        $('.simplemanagement-addstory').each(function() {
            var container = $(this);
            var link = $('a', container);
            var wrapper = $('div.simplemanagement-addstory-form-wrapper');
            if($('dl.portalMessage', wrapper).length > 0){
                wrapper.css('display', 'block');
                add_form_link.addClass('open');
            }

            link.bind('click', function(evt) {
                $(this).toggleClass('open');
                evt.preventDefault();
                wrapper.toggle("slow");
            });
        });

        $('#overview ul.tabs').tabs("#overview div.panes > div");


        $('#project-iterations').tabs(
            "#project-iterations div.pane",
            {tabs: 'h2', effect: 'slide', initialIndex: 1}
        );

        $('.quickedit').prepOverlay({
            subtype: 'iframe',
            closeselector: '.button-field',
            width:'70%'
        });

        $('.story-quickview').prepOverlay({
            subtype: 'ajax',
            filter: common_content_filter,
            formselector: 'form#booking_form',
            width:'80%'
        });

        $('.quickview').prepOverlay({
            subtype: 'ajax',
            filter: common_content_filter,
            width:'50%'
        });


        function updateStoryPosition(event, ui) {
            position = ui.item.index();
            item_id = ui.item.attr('id');
            $.getJSON(
                './story_move?story_id=' + item_id + '&position=' + position,
                function(data){
                    if(data['success'] === false) {
                        alert(data['error']);
                    }
                }
           );
        }

        $( ".portaltype-iteration .sortable" ).sortable({
            update: updateStoryPosition,
            tolerance: 'pointer',
            distance: 5,
            opacity: 0.5,
            revert: true
        });


        $('.status').tooltip({
            events: {
                def: "click,blur"
            },

            onBeforeShow: function(){
                var tip = this.getTip();
                tip.empty();
                var trigger = this.getTrigger();
                var url = trigger.attr('href');
                var story_container = $(trigger).parents("li");
                $.get(url + '/wf_actions', function(data) {
                    tip.html(data);
                    var links = $(tip).find('a');
                    links.bind('click', function(evt){
                        $.getJSON($(this).attr('href'), function(data) {
                            if(data === false) {
                                alert('An error occurred');
                            }
                            else {
                                story_container.removeClass(
                                    'done in_progress suspended todo');
                                story_container.addClass(data);
                                tip.hide();
                            }
                        });
                        evt.preventDefault();
                    });
                });
            }
        });

    });
})(jQuery);
