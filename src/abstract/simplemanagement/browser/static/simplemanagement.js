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

  function get_transition_link(data, url, trigger) {
    var link = $('<a></a>');
    var dest_status = data['destination'];
    var story_container = trigger.parents("li");
    link.attr('href', url + '/change_status?action=' + data['id']);
    link.attr('title', data['description']);
    link.text(data['title']);
    link.bind('click', function(event){
      var el = $(this);
      $.getJSON(el.attr('href'), function(data) {
        if (data == true) {
          story_container.removeClass('done in_progress suspended todo');
          story_container.addClass(dest_status);
        } else {
          alert('An error occurred');
        }

      });
      event.preventDefault();
    });
    return link;
  }

  $('.status').tooltip({
    events: {
      def: "click,blur",
    },
    onBeforeShow: function(){
      var tip = this.getTip();
      var trigger = this.getTrigger();
      var url = trigger.attr('href');
      var content = $('<div></div>');
      $.getJSON(url + '/wf_actions', function(data){
        for (var i=0; i<data.length; i++){
          content.append(get_transition_link(data[i], url, trigger));
        }
        tip.html(content);
      })
    }

  });

});
