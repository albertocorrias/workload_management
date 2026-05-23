
$(document).ready(function() {
$('#TABLE_1').DataTable( {
       dom:     "<'row'<'col-sm-3'l><'col-sm-6 text-center'B><'col-sm-3'f>>" +
                "<'row'<'col-sm-12'tr>>" +
                "<'row'<'col-sm-5'i><'col-sm-7'p>>",
        buttons: [
        'copy', 'csv', 'excel', 'pdf', 'print'
    ],
    paging: true

});

$('#TABLE_2').DataTable( {
    dom:     "<'row'<'col-sm-3'l><'col-sm-6 text-center'B><'col-sm-3'f>>" +
            "<'row'<'col-sm-12'tr>>" +
            "<'row'<'col-sm-5'i><'col-sm-7'p>>",
    buttons: [
    'copy', 'csv', 'excel', 'pdf', 'print'
],
paging: true
});

$('#TABLE_WORKLOAD_INDEX').DataTable( {
    dom:     "<'row'<'col-sm-3'l><'col-sm-6 text-center'B><'col-sm-3'f>>" +
            "<'row'<'col-sm-12'tr>>" +
            "<'row'<'col-sm-5'i><'col-sm-7'p>>",
    buttons: [
    'copy', 'csv', 'excel', 'pdf', 'print'
],
paging: true
});

$('#FACULTY_TABLE_REPORT').DataTable( {
    dom:     "<'row'<'col-sm-3'l><'col-sm-6 text-center'B><'col-sm-3'f>>" +
            "<'row'<'col-sm-12'tr>>" +
            "<'row'<'col-sm-5'i><'col-sm-7'p>>",
    buttons: [
    'copy', 'csv', 'excel', 'pdf', 'print'
],
paging: true
});


} );