$(document).ready(function(){

  $('#overview ul.tabs').tabs("#overview div.panes > div");


  $('#project-iterations').tabs(
      "#project-iterations div.pane",
      {tabs: 'h2', effect: 'slide', initialIndex: 1}
    );

  $('.quickedit').prepOverlay({
    subtype: 'iframe',
    closeselector: '.button-field',
    width:'70%',
  });

  $('.quickview').prepOverlay({
      subtype: 'ajax',
      filter: common_content_filter,
      formselector: 'form#booking_form',
      width:'80%'
  });

  function updateStoryPosition(event, ui) {
    // TODO
  }

  $( ".sortable" ).sortable({
    update: updateStoryPosition,
    tolerance: 'pointer',
    distance: 5,
    opacity: 0.5,
    revert: true
  });


  $('.status').tooltip({
    events: {
      def: "click,blur",
    },

    onBeforeShow: function(){
      var tip = this.getTip();
      tip.empty();
      var trigger = this.getTrigger();
      var url = trigger.attr('href');
      var story_container = $(trigger).parents("li");
      // var dest_status = data['destination'];
      $.get(url + '/wf_actions', function(data) {
        tip.html(data);
        // alert(story_container.attr('class'));
        var links = $(tip).find('a');
        links.bind('click', function(evt){
          evt.preventDefault()
          $.getJSON($(this).attr('href'), function(data) {
            if (data == false) {
              alert('An error occurred');
            } else {
              story_container.removeClass('done in_progress suspended todo');
              story_container.addClass(data);
              tip.hide();
            }
          });
        });
      });
    }

  });

});
