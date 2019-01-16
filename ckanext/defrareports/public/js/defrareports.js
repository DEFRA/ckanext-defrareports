$(document).ready(function(){
  $('.expando-report').on('click', function(){
    var chev = $(this).siblings('ul').get(0)
    $(chev).toggle();
  });
});
