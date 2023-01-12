function check_box() {
    if ($('.form-check-input').is(":checked"))
        $("#add").hide()
    else
        $("#add").show()
}



$(document).ready(function() {

    var $submit = $("#action_dropdown").hide(),
        $cbs = $('input[name="check-box"]').click(function() {
            $submit.toggle( $cbs.is(":checked") );
        });

});

function del_rec(id){
    $('#exampleModalCenter'+id).modal('show');
    $('#modal_del'+id).attr('href','')
    $('#modal_del'+id).attr('href','/delete_customer/'+id)
 }

function del_fun(){
        $('#stu_ids_submit').click()
    }




var admin_ids = [];
textbox2 = document.getElementById("rec_ids")

$(".form-check-input").click(function(){
    admin_ids=[];
    $(".form-check-input").each(function(){
        if($(this).is(":checked")){
        admin_ids.push($(this).val());
        }
        });
        console.log(admin_ids);
        textbox2.value = admin_ids

    });


