

/* Nombre de fichero en formulario de subida */

$(".custom-file-input").on("change", function() {
  var file = $(this).val().split("\\").pop();
  $(this).siblings(".custom-file-label").addClass("selected").html(file);
});
/*
$(document).ready(function(){
    $(function(){
        var current = location.pathname;
        $('#navbarNavAltMarkup a').each(function(){
            var $this = $(this);
            // if the current path is like this link, make it active
            if($this.attr('href').indexOf(current) !== -1){
                $this.addClass('active');
            }
        })
    })
});
*/

/*
$(document).ready(function(){
    $('.navbar-nav .nav-item').click(function(){
        $('.nav-item').removeClass('active');
        $(this).closest('.nav-item').siblings();
        $(this).closest('.nav-item').addClass('active');
    });
});
*/


