(function() {
  'use strict';
    $(document).ready(function () {

    var datePickerElements = $('.date-picker');

    datePickerElements.each(function (e) {
      var calendarSelector = $("#" + $(this).attr('id'));
      var calendarInput = "#" + $(this).attr('id') + "-input";
      var selectedValue = document.getElementById($(this).attr('id') + '-input').value;
      var selectedDate = new Date(selectedValue);

      var calendarOptions = {
        showButtonPanel: true,
        dateFormat: "yy-mm-dd",
        altField: calendarInput
      };

      calendarSelector.datepicker(calendarOptions);
      calendarSelector.datepicker('setDate', selectedDate);

      calendarSelector.on('change', function(evt){
        evt.preventDefault();
        calendarSelector.datepicker('setDate', new Date(evt.target.value));
      });
    });
  });
})($);