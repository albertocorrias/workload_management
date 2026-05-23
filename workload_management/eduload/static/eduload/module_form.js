$(document).ready(function() {

    $('#id_total_hours').parents('p').hide() //Note the "id_" is Django's default for assigning id to HTML items in forms
    $('#id_total_hours').disabled=true
    $('#id_manual_hours_checked')[0].addEventListener('change', (event) => {
        let hours_field = $('#id_total_hours').parents('p');
        
        if (event.target.checked) {
            hours_field.show();
            $('#id_total_hours').disabled=false
        } else {
            hours_field.hide();
            $('#id_total_hours').disabled=true
        }
    })
});