function editClient(){

edit_btn = document.getElementById('edit_button');
edit_btn.parentNode.removeChild(edit_btn);

document.getElementById('update_button').hidden = false;
document.getElementById('discard_button').hidden = false;
document.getElementById('back_button').style.display = "none";
//action_buttons = document.getElementById("action_buttons")
//action_buttons.style.backgroundColor = "#141619";


hide_table = document.getElementById('hide_table');
hide_table.parentNode.removeChild(hide_table);

var form_editable = document.getElementsByClassName('form_editable');
    for(var i = 0; i < form_editable.length; i++) {
    form_editable[i].hidden = false;
}
}



