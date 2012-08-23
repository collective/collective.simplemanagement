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
      var tip = this.getTip()
      var content = '<div><a href="#">Start</a><a href="#">Complete</a><a href="#">Suspend</a></div>';
      tip.html(content);
    }

  });

});
