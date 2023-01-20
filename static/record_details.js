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
if (!(document.getElementById('update_btn_file'))){
    //pass
}
else{
document.getElementById('update_btn_file').hidden = false;
}

if (!(document.getElementById('upload_file'))){
    //pass
}
else{
document.getElementById('upload_file').hidden = false;

}


if (!(document.getElementById('no_attachment'))){
    //pass
}
else{
document.getElementById('no_attachment').hidden = true;

}




action_buttons = document.getElementById("action_buttons")
action_buttons.style.backgroundColor = "#141619";
//document.body.style.backgroundColor = "#141619";



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


var status = document.querySelectorAll("status").innerText;


$(document).ready(function(){
    $( ".status:contains('Pending')" ).css( "color", "white" );
    $( ".status:contains('Pending')" ).css( "background-color", "red" );
    $( ".status:contains('Pending')" ).css( "font-weight" , "bold" );
})

$(document).ready(function(){
    $( ".status:contains('Cancel')" ).css( "color", "white" );
    $( ".status:contains('Cancel')" ).css( "background-color", "#8e8df4" );
    $( ".status:contains('Cancel')" ).css( "font-weight" , "bold" );
})

$(document).ready(function(){
    $( ".status:contains('Received')" ).css( "color", "white" );
    $( ".status:contains('Received')" ).css( "background-color", "green" );
    $( ".status:contains('Received')" ).css( "font-weight" , "bold" );
})


status_name = document.getElementById('status')
if (status_name.innerHTML == "Received" || status_name.innerHTML == "Cancelled"){
console.log('status_name')
    edit_button = document.getElementById('edit_button');
    edit_button.parentNode.removeChild(edit_button);
}



//file upload
$('#file-upload').change(function() {
  var i = $(this).prev('label').clone();
  var file = $('#file-upload')[0].files[0].name;
  $(this).prev('label').text(file);
});

$('#file1-upload').change(function() {
  var i = $(this).prev('label').clone();
  var file = $('#file1-upload')[0].files[0].name;
  $(this).prev('label').text(file);
});


function new_file_upload(){
document.getElementById("update_file").hidden = false
document.getElementById("current_file").hidden = true
document.getElementById("update_btn_file").hidden = true
}




$('.client_name').prop('hidden', true);