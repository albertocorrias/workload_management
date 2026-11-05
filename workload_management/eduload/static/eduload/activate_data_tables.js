
$(document).ready(function() {

    $('.eduload-table').DataTable( {
    dom:    "<'row mb-3'<'col-sm-3'l><'col-sm-6 text-center'B><'col-sm-3'f>>" +
            "<'row'<'col-sm-12'tr>>" +
            "<'row'<'col-sm-5'i><'col-sm-7'p>>",
    buttons: [
    'copy', 'csv', 'excel', 'pdf', 'print'
],
paging: true,
buttons: [
    {
        extend: 'copy',
        className: 'btn btn-sm btn-secondary mx-1'
    },
    {
        extend: 'csv',
        className: 'btn btn-sm btn-info text-white mx-1'
    },
    {
        extend: 'excel',
        className: 'btn btn-sm btn-success mx-1'
    },
    {
        extend: 'pdf',
        className: 'btn btn-sm btn-danger mx-1'
    },
    {
        extend: 'print',
        className: 'btn btn-sm btn-dark mx-1'
    }
]
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