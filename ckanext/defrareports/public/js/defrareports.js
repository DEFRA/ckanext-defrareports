var monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

$(function() {
  $('[data-toggle="tooltip"]').tooltip();

  if ($('#report-table').length > 0) {
    $('#report-table').tablesorter({
      dateFormat: 'uk',
    });
  }
  $('.js-auto-submit').change(function () {
      $(this).closest('form').submit();
  });

  // Hide dataset name tooltip after accordion has closed
  $('.worst-offender-panel').on('hidden.bs.collapse', function() {
    $(this).prev().find('[data-toggle="tooltip"]').tooltip('hide');
  });
});

