//remove disable form
function hideDisable(){

document.querySelector('#edit_button').style.display = "none";

//document.getElementById('update_discard_button').style.display = "block";
document.getElementById('update_discard_button_for_bill_details').style.display = "block";
document.getElementById('cancelled_button_before').style.display = "none";
document.getElementById('cancelled_button_after').style.display = "block";
document.getElementById('back_button').style.display = "none";
//document.getElementById('discard_button').style.display = "block";
//document.getElementById('cancelled_button').hidden = false;
document.getElementById('voucher_book_action_button').hidden = false;
document.getElementById('voucher_book').hidden = true;


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




//action_buttons = document.getElementById("action_buttons")
//action_buttons.style.backgroundColor = "#141619";




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
    $( ".status:contains('Pending')" ).css( "background-color", "#ffc107" );
    $( ".status:contains('Pending')" ).css( "font-weight" , "bold" );
})

$(document).ready(function(){
    $( ".status:contains('Cancel')" ).css( "color", "white" );
    $( ".status:contains('Cancel')" ).css( "background-color", "red" );
    $( ".status:contains('Cancel')" ).css( "font-weight" , "bold" );
})

$(document).ready(function(){
    $( ".status:contains('Received')" ).css( "color", "white" );
    $( ".status:contains('Received')" ).css( "background-color", "green" );
    $( ".status:contains('Received')" ).css( "font-weight" , "bold" );
})




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


function client_unchanged(){
    document.getElementById('alert_client').hidden = false;
}



$('.client_name').prop('hidden', true);



var elementPosition = $('#action_buttons').offset();

$(window).scroll(function(){
        if($(window).scrollTop() > elementPosition.top){
              $('#action_buttons').css('position','fixed').css('top','0').css('background-color','#212529').css('width','100%');
              $('#voucher_book').css('color','white');
              $('#voucher_book_action_button').css('color','white');
              $('#edit_button').css('margin-left','185px');
              $('#cancelled_button_before').css('margin-right','140px');
              $('#cancelled_button').css('margin-right','169px');
              $('#voucher_book_action_button_image').css('margin-left','223px');
              $('#total_vouchers_after').css('margin-left','223px');
              $('#btn-toolbar').css('margin-left','145px');
//              $('#action_buttons').css('background-color','red');
        } else {
            $('#action_buttons').css('position','static').css('background-color','#F8F9FA').css('width','75%');
            $('#voucher_book').css('color','black');
            $('#voucher_book_action_button').css('color','black');
            $('#edit_button').css('margin-left','');
            $('#cancelled_button_before').css('margin-right','');
            $('#cancelled_button').css('margin-right','');
            $('#voucher_book_action_button_image').css('margin-left','162px');
            $('#total_vouchers_after').css('margin-left','162px');
            $('#btn-toolbar').css('margin-left','');

        }
});




let gst_select = document.getElementById('gst');
let amount_by_user = document.getElementById('amount_by_user');
let final_deal_including_gst = document.getElementById('final_deal_including_gst');

//console.log(final_deal_amount)
gst_select.onchange = function () {
    gst_no = gst_select.value;

    if (gst_no == 12){
        final_deal_amount_gst = parseFloat((12 / 100) * amount_by_user.value)

        final_deal_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)
        if (gst_inc_record_details){
            gst_inc_record_details.style.display ="block";
        }

    }
    if (gst_no == 18){
        final_deal_amount_gst = parseFloat((18 / 100) * amount_by_user.value)

        final_deal_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)
        if (gst_inc_record_details){
            gst_inc_record_details.style.display ="block";
        }
    }
    if (gst_no == 5){
        final_deal_amount_gst = parseFloat((5 / 100) * amount_by_user.value)

        final_deal_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)
        if (gst_inc_record_details){
            gst_inc_record_details.style.display ="block";
        }
    }
    if (gst_no == 28){
        final_deal_amount_gst = parseFloat((28 / 100) * amount_by_user.value)

        final_deal_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)
        if (gst_inc_record_details){
            gst_inc_record_details.style.display ="block";
        }
    }
}


window.onload = function () {
    gst_no = gst_select.value;

    if (gst_no == 12){
        final_deal_amount_gst = parseFloat((12 / 100) * amount_by_user.value)

        final_deal_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)
    }
    if (gst_no == 18){
        final_deal_amount_gst = parseFloat((18 / 100) * amount_by_user.value)

        final_deal_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)
    }
    if (gst_no == 5){
        final_deal_amount_gst = parseFloat((5 / 100) * amount_by_user.value)

        final_deal_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)
    }
    if (gst_no == 28){
        final_deal_amount_gst = parseFloat((28 / 100) * amount_by_user.value)

        final_deal_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)
    }
}




gst_inc_record_details = document.getElementById('final_deal_including_gst')
amount_by_user.onchange = function () {
    gst_no = gst_select.value;

    if (gst_no == 12){
        final_deal_amount_gst = parseFloat((12 / 100) * amount_by_user.value)

        final_deal_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)

        if (gst_inc_record_details){
            gst_inc_record_details.style.display ="block";
        }

    }
    if (gst_no == 18){
        final_deal_amount_gst = parseFloat((18 / 100) * amount_by_user.value)

        final_deal_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)

        if (gst_inc_record_details){
            gst_inc_record_details.style.display ="block";
        }
    }
    if (gst_no == 5){
        final_deal_amount_gst = parseFloat((5 / 100) * amount_by_user.value)

        final_deal_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)

        if (gst_inc_record_details){
            gst_inc_record_details.style.display ="block";
        }
    }
    if (gst_no == 28){
        final_deal_amount_gst = parseFloat((28 / 100) * amount_by_user.value)

        final_deal_including_gst.value = parseInt(amount_by_user.value) + parseInt(final_deal_amount_gst)
        if (gst_inc_record_details){
            gst_inc_record_details.style.display ="block";
        }
    }


}
