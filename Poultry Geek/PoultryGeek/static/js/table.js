
/* Ocultar divs */

        // Mostrar tabla
    function mostrar_nav_table(){
        //document.getElementById('table-variable-selector').style.display="none";
        document.getElementById('table-container-stats').style.display="none";
        document.getElementById('table-container-graphics').style.display="none";
        document.getElementById('table-container-table').style.display="block";
    }

        // Mostrar Estadísticas
    function mostrar_nav_stats(){
        document.getElementById('table-container-table').style.display="none";
        document.getElementById('table-container-graphics').style.display="none";
        //document.getElementById('table-variable-selector').style.display="block";
        document.getElementById('table-container-stats').style.display="block";
    }

        // Mostrar Gráficos
    function mostrar_nav_graphics(){
        document.getElementById('table-container-table').style.display="none";
        document.getElementById('table-container-stats').style.display="none";
        //document.getElementById('table-variable-selector').style.display="block";
        document.getElementById('table-container-graphics').style.display="flex";
    }

/* DataTables */

    // Para que se vean bien las tablas. Inicializa la tabla como table_id
    $(document).ready( function () {
        var t = $('#table_id').DataTable( {

    //        l - length changing input control
    //        f - filtering input
    //        t - The table!
    //        i - Table information summary
    //        p - pagination control
    //        r - processing display element

            // Imprimir
            dom: 'Blftipr',
            buttons: [
            {
                extend: 'print',
                text: 'Imprimir',/*
                exportOptions: {
                    modifier: {
                        page: 'current',
                    }
                }*/
            },
            ],

            // Traducción
            language: {
                paginate: {
                    first:      "Primero",
                    previous:   "Anterior",
                    next:       "Siguiente",
                    last:       "Último"
                },
                search:         "Buscar:",
                info:           "Nº total de camadas encontradas: _TOTAL_.", /*_START_ - _END_*/
                lengthMenu:     "Mostrar  _MENU_  camadas",
                infoFiltered:   " (de _MAX_ camadas en total)",
            },



            // Scroll
            deferRender:    true,
            scrollY:        425,
            scrollX:        425,
            scrollCollapse: true,
            scroller:       true,
            stateSave:      true,

            columnDefs: {
                searchable: false,
                orderable: false,
                targets: 0
            },
            order: [[ 1, 'asc' ]],

        } );

        t.on( 'order.dt search.dt', function () {
            t.column(0, {search:'applied', order:'applied'}).nodes().each( function (cell, i) {
                cell.innerHTML = i+1;
            } );
        } ).draw();
    });


    // Para que se vean bien las tablas. Inicializa la tabla como table_id
    $(document).ready( function () {
        $('#table_stats').DataTable( {

    //        l - length changing input control
    //        f - filtering input
    //        t - The table!
    //        i - Table information summary
    //        p - pagination control
    //        r - processing display element

            // Imprimir
            dom: 'Brp',
            buttons: [
            {
                extend: 'print',
                text: 'Imprimir',
                exportOptions: {
                    modifier: {
                        page: 'current'
                    }
                }
            },
            ],

            // Traducción
            language: {
                paginate: {
                    first:      "Primero",
                    previous:   "Anterior",
                    next:       "Siguiente",
                    last:       "Último"
                },
                info:           "Nº total de camadas encontradas: _TOTAL_.", /*_START_ - _END_*/
                lengthMenu:     "Mostrar  _MENU_  camadas",
                infoFiltered:   " (de _MAX_ camadas en total)",
//                thousands: ";",
//                decimal: ",",
            },

            // Scroll
            deferRender:    true,
            scrollY:        425,
            scrollX:        425,
            scrollCollapse: true,
            scroller:       true,
            stateSave:      true,
        } );
    });


/* Para que un elemento del panel de navegación cambie si está activo */

    $(document).ready(function(){
        $('#table-container-nav a').click(function(){
            $('#table-container-nav a').removeClass("active");
            $('#table-container-nav a').css({"color" : "grey"});
            $(this).addClass("active");
            $(this).css({"color" : "green"});
        });
    });

    $(document).ready( function () {
        document.getElementById('table_id').style.margin=0;
    } );


//
//    $(document).ready( function () {
//        $('.dataTables_scrollBody').addClass("container-fluid");
//    } );
/*
$('#table_id').DataTable( {
    language: {
        processing:     "Traitement en cours...",
        search:         "Rechercher&nbsp;:",
        lengthMenu:    "Afficher _MENU_ &eacute;l&eacute;ments",
        info:           "Affichage de l'&eacute;lement _START_ &agrave; _END_ sur _TOTAL_ &eacute;l&eacute;ments",
        infoEmpty:      "Affichage de l'&eacute;lement 0 &agrave; 0 sur 0 &eacute;l&eacute;ments",
        infoFiltered:   "(filtr&eacute; de _MAX_ &eacute;l&eacute;ments au total)",
        infoPostFix:    "",
        loadingRecords: "Chargement en cours...",
        zeroRecords:    "Aucun &eacute;l&eacute;ment &agrave; afficher",
        emptyTable:     "Aucune donnée disponible dans le tableau",
        paginate: {
            first:      "Premier",
            previous:   "Pr&eacute;c&eacute;dent",
            next:       "Suivant",
            last:       "Dernier"
        },
        aria: {
            sortAscending:  ": activer pour trier la colonne par ordre croissant",
            sortDescending: ": activer pour trier la colonne par ordre décroissant"
        }
    }
} );
*/
