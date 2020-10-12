//Para que se vean bien las tablas

$(document).ready( function () {
    $('#table_id').DataTable();
});

//Para que un elemento del panel de navegación cambie si está activo
$(document).ready(function(){
    $('a').click(function(){
        $('a').removeClass("active");
        $(this).addClass("active");
    });
});

// Add the following code if you want the name of the file appear on select
$(".custom-file-input").on("change", function() {
  var file = $(this).val().split("\\").pop();
  $(this).siblings(".custom-file-label").addClass("selected").html(file);
});