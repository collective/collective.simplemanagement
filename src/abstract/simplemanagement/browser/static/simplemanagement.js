$(document).ready(function(){

  $('#overview ul.tabs').tabs("#overview div.panes > div");


  $('#project-iterations').tabs(
      "#project-iterations div.pane",
      {tabs: 'h2', effect: 'slide', initialIndex: 1}
    );

  $('.quickedit').prepOverlay({
    subtype: 'iframe',
    closeselector: '.button-field',
    width:'50%',
  });


  $('.quickview').prepOverlay({
      subtype: 'ajax',
      filter: common_content_filter,
      width:'80%'
  });

  $( ".sortable" ).sortable({
    distance: 5,
    opacity: 0.5,
    revert: true
  });

 // + '?ajax_load=1&ajax_include_head=1'
});
