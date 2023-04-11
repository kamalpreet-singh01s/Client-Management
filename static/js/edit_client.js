function editClient() {

    let edit_btn = document.getElementById('edit_button');
    edit_btn.parentNode.removeChild(edit_btn);

    document.getElementById('update_button').hidden = false;
    document.getElementById('discard_button').hidden = false;
    document.getElementById('back_button').style.display = "none";
//action_buttons = document.getElementById("action_buttons")
//action_buttons.style.backgroundColor = "#141619";


    let hide_table = document.getElementById('hide_table');
    hide_table.parentNode.removeChild(hide_table);

    let form_editable = document.getElementsByClassName('form_editable');
    for (const element of form_editable) {
        element.hidden = false;
    }
}



