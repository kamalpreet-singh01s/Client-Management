//remove disable form
function hideDisable(){
edit_btn = document.getElementById('edit_button');
edit_btn.parentNode.removeChild(edit_btn);

document.getElementById('update_button').hidden = false;
document.getElementById('discard_button').hidden = false;
document.getElementById('received_button').hidden = false;
document.getElementById('cancelled_button').hidden = false;

document.getElementById('client_details').hidden = false;
document.getElementById('bill_details').hidden = false;


action_buttons = document.getElementById("action_buttons")
action_buttons.style.backgroundColor = "#141619";
document.body.style.backgroundColor = "#141619";

document.getElementById('add_file').hidden = false;


hide_table = document.getElementById('hide_table');
hide_table.parentNode.removeChild(hide_table);

hide_table2 = document.getElementById('hide_table2');
hide_table2.parentNode.removeChild(hide_table2);

document.getElementById("client_details").hidden = false;
document.getElementById("bill_details").hidden = false;


var form_editable = document.getElementsByClassName('form_editable');
    for(var i = 0; i < form_editable.length; i++) {
    form_editable[i].hidden = false;
}
}





function remove_pdf_file(){


document.getElementById('current_pdf').hidden = true;


document.getElementById('add_file').hidden=true;


document.getElementById('pdf_upload').hidden = false;
}


//preview_file
 function readURL(input) {
        document.getElementById('pdf_image').hidden = false;
        document.getElementById('x').hidden = false;

document.getElementById('upload').hidden = true;
        }

function remove_selected_file(){
    selected_pdf = document.getElementById('selected_pdf');
selected_pdf.parentNode.removeChild(selected_pdf);
document.getElementById('x').hidden = true;
document.getElementById('upload').hidden = false;

}


status_name = document.getElementById('status')
if (status_name.innerHTML == "Received" || status_name.innerHTML == "Cancelled"){
console.log('status_name')
    edit_button = document.getElementById('edit_button');
    edit_button.parentNode.removeChild(edit_button);
}



$('.client_name').prop('hidden', true);