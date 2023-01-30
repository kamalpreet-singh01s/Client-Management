$("#amount").keyup(function () {
    if($(this).val() == "") {
        $("#approve_button").hide();
        $("#cancel_button").hide();
    } else {
        // Text found
        $("#cancel_button").show();
        $("#approve_button").show();
    }
});



//    document.getElementById('see_all_for_approved').hidden = false;
//    see_all_for_not_approved = document.getElementById('see_all_for_not_approved');
//    see_all_for_not_approved.parentNode.removeChild(see_all_for_not_approved);
//
//    document.getElementById('cancelled_button_after').style.display = "block";

//else{
//    document.getElementById('see_all_for_not_approved').hidden = false;
//}


