function editClient() {

    let edit_btn = document.getElementById('edit_button');
    edit_btn.parentNode.removeChild(edit_btn);

    document.getElementById('update_button').hidden = false;
    document.getElementById('discard_button').hidden = false;
    document.getElementById('change_password').hidden = false;
    document.getElementById('back_button').style.display = "none";


    let hide_table = document.getElementById('hide_table');
    hide_table.parentNode.removeChild(hide_table);

    let form_editable = document.getElementsByClassName('form_editable');
    for (const element of form_editable) {
        element.hidden = false;
    }
}


//update_btn = document.getElementById("update_button")
//
//update_btn.onclick(function(){

function check_error() {

    let div = document.querySelector('div')
    // if (div.ClassList.contains('error')) {
    //     $("#edit_button").click()
    // } else {
    //     $("#edit_button").click()
    // }
    $("#edit_button").click()
}

//
//})





