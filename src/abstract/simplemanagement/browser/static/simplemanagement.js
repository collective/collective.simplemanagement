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

});
