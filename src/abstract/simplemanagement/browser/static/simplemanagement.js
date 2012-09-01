(function($) {
    if ((typeof window.simplemanagement) === "undefined") {
        window.simplemanagement = {};
    }

    simplemanagement.Planner = function(element) {
        this._init(element);
    };

    simplemanagement.Planner.prototype = {
    };

    simplemanagement.planners = [];

    $(document).ready(function(){

        $('.-simplemenagement-planner').each(function() {
            simplemanagement.planners.push(
                new simplemanagement.Planner($(this)));
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
