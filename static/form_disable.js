//remove disable form
function hideDisable(){
edit_btn = document.getElementById('edit_button');
edit_btn.parentNode.removeChild(edit_btn);

document.getElementById('update_button').hidden = false;
document.getElementById('discard_button').hidden = false;

document.getElementById('received_button').hidden = false;
document.getElementById('cancelled_button').hidden = false;
document.getElementById('add_file').hidden = false;

action_buttons = document.getElementById("action_buttons")
action_buttons.style.backgroundColor = "#141619";
document.body.style.backgroundColor = "#141619";

//visible_customer_name = document.getElementById('visible_customer_name');
//visible_customer_name.parentNode.removeChild(visible_customer_name);
//
//visible_email = document.getElementById('visible_email');
//visible_email.parentNode.removeChild(visible_email);
//
//visible_phone = document.getElementById('visible_phone');
//visible_phone.parentNode.removeChild(visible_phone);
//
//visible_address = document.getElementById('visible_address');
//visible_address.parentNode.removeChild(visible_address);
//
//visible_final_deal = document.getElementById('visible_final_deal');
//visible_final_deal.parentNode.removeChild(visible_final_deal);
//
//visible_gst = document.getElementById('visible_gst');
//visible_gst.parentNode.removeChild(visible_gst);
//
//visible_content_advt = document.getElementById('visible_content_advt');
//visible_content_advt.parentNode.removeChild(visible_content_advt);
//
//visible_date_of_order = document.getElementById('visible_date_of_order');
//visible_date_of_order.parentNode.removeChild(visible_date_of_order);
//
//dop = document.getElementById('dop');
//dop.parentNode.removeChild(dop);
//
//bill_date = document.getElementById('bill_date');
//bill_date.parentNode.removeChild(bill_date);
//
//status_name = document.getElementById('status_name');
//status_name.parentNode.removeChild(status_name);


hide_table = document.getElementById('hide_table');
hide_table.parentNode.removeChild(hide_table);

document.getElementById("client_details").hidden = false;
document.getElementById("bill_details").hidden = false;

hide_table = document.getElementById('hide_table2');
hide_table.parentNode.removeChild(hide_table);



var form_editable = document.getElementsByClassName('form_editable');
    for(var i = 0; i < form_editable.length; i++) {
    form_editable[i].hidden = false;
}
}


status_name = document.getElementById('status').value
if (status_name == "Received"){
    edit_btn = document.getElementById('edit_button');
    edit_btn.parentNode.removeChild(edit_btn);
}
console.log(status_name)




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
if (status_name.innerText == "Received" || status_name.innerText == "Cancelled"){
console.log("test")
    edit_btn = document.getElementById('edit_button');
    edit_btn.parentNode.removeChild(edit_btn);
}