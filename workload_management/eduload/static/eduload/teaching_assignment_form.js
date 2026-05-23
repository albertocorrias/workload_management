

$(document).ready(function() {

    var all_weekly_assignments = document.getElementsByClassName("teaching_assignment_weekly_hours")
    var all_manual_assignments = document.getElementsByClassName("teaching_assignment_manual_hours")
    
    //disable the manual hours entry first
    //hide the manual hours, show the weekly ones
    for (let idx = 0; idx < all_weekly_assignments.length; idx++){
        all_weekly_assignments[idx].parentElement.style.display = "block"
    }
    for (let idx = 0; idx < all_manual_assignments.length; idx++){
        all_manual_assignments[idx].parentElement.style.display = "none"
    }

    //get the checkbox
    manual_hrs_checkboxes = document.getElementsByClassName("teaching_assignment_radio_buttons_style")
    
    //add the event to the checkbox elements
    for (let idx = 0; idx < manual_hrs_checkboxes.length; idx++) {
        single_checkbox = manual_hrs_checkboxes[idx]

        single_checkbox.addEventListener('change', (event) => {

            for (let i = 0; i < single_checkbox.parentElement.length; i++) {
                console.log(single_checkbox.parentElement[i].tagName);
            }
            single_checkbox.parentElement.parentElement.classList.remove("activated_option")
            switch (event.target.value) {
                case 'yes':
                    //show the manual hours, hide the weekly ones
                    for (let idx = 0; idx < all_weekly_assignments.length; idx++){
                        all_weekly_assignments[idx].parentElement.style.display = "none"
                    }
                    for (let idx = 0; idx < all_manual_assignments.length; idx++){
                        all_manual_assignments[idx].parentElement.style.display = "block"
                    }
                    break;
                case 'no' :
                    //hide the manual hours, show the weekly ones
                    for (let idx = 0; idx < all_weekly_assignments.length; idx++){
                        all_weekly_assignments[idx].parentElement.style.display = "block"
                    }
                    for (let idx = 0; idx < all_manual_assignments.length; idx++){
                        all_manual_assignments[idx].parentElement.style.display = "none"
                    }
                    break;
                        
            } 
        })

    }

});