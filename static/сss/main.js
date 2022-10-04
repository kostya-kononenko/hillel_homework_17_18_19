$(function () {
  /* Functions */
  var loadForm = function () {
    var btn = $(this);
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        $("#contact .modal-content").html("");
        $("#contact").modal("show");
      },
      success: function (data) {
        $("#contact .modal-content").html(data.html_form);
      }
    });
  };

  var saveForm = function () {
    var form = $(this);
    $.ajax({
      url: form.attr("action"),
      data: form.serialize(),
      type: form.attr("method"),
      dataType: 'json',
      success: function (data) {
        if (data.form_is_valid) {
          // $("#contact").modal("hide");
          $(".container-fluid").prepend(data.html_contact_msg);
          $("#contact").modal("hide");
        }
        else {
          $("#contact .modal-content").html(data.html_form);
        }
      }
    });
    return false;
  };
  /* Binding */
  $(".js-contact").click(loadForm);
  $("#contact").on("submit", ".jx-jx", saveForm);
});