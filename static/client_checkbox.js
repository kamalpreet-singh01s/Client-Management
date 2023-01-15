
var cli_values=[];

textbox = document.getElementById("rec_ids")

$(".form-check-input").click(function(){
    cli_values=[];
    $(".form-check-input").each(function(){
        if($(this).is(":checked")){
        cli_values.push($(this).val());
        }
        });
        console.log(cli_values);
        textbox.value = cli_values

    });

//$(document).ready(function() {
//
//    var $submit = $("#stu_ids_submit").hide(),
//        $cbs = $('input[name="check-box"]').click(function() {
//            $submit.toggle( $cbs.is(":checked") );
//        });
//
//});



var get_check_for_csv=[];

textbox3 = document.getElementById("check_rec_ids")

$(".form-check-input").click(function(){
    get_check_for_csv=[];
    $(".form-check-input").each(function(){
        if($(this).is(":checked")){
        get_check_for_csv.push($(this).val());
        }


        });
        console.log(get_check_for_csv);
        textbox3.value = get_check_for_csv

    });






$(document).ready(function() {

    var $submit = $("#check_rec_ids_btn").hide(), $update_check = $("#update_check").hide(), $update_label = $("#update_label").hide(),
        $cbs = $('input[name="check-box"]').click(function() {
            $submit.toggle( $cbs.is(":checked") ) && $update_check.toggle( $cbs.is(":checked") ) && $update_label.toggle( $cbs.is(":checked") );
        });

});






function check_box() {
    if ($('.form-check-input').is(":checked"))
        $("#add").hide()
    else
        $("#add").show()
}


function del_fun(){
        $('#stu_ids_submit').click()
    }

$(document).ready(function() {

    var $submit = $("#action_dropdown").hide(),
        $cbs = $('input[name="check-box"]').click(function() {
            $submit.toggle( $cbs.is(":checked") );
        });

});