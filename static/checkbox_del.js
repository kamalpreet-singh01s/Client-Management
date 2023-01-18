
var values=[];

textbox = document.getElementById("rec_ids")

$(".form-check-input").click(function(){
    values=[];
    $(".form-check-input").each(function(){
        if($(this).is(":checked")){
        values.push($(this).val());
        }
        });
        console.log(values);
        textbox.value = values

    });


var class_id = [];
textbox2 = document.getElementById("send_rec_ids")

$(".form-check-input").click(function(){
    class_id=[];
    $(".form-check-input").each(function(){
        if($(this).is(":checked")){
        class_id.push($(this).val());
        }
        });
        console.log(class_id);
        textbox2.value = class_id

    });


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


//$(document).ready(function() {
//
//    var $submit = $("#stu_ids_submit").hide(),
//        $cbs = $('input[name="check-box"]').click(function() {
//            $submit.toggle( $cbs.is(":checked") );
//        });
//
//});
//
//$(document).ready(function() {
//
//    var $submit = $("#class_ids_submit").hide(),
//        $cbs = $('input[name="check-box"]').click(function() {
//            $submit.toggle( $cbs.is(":checked") );
//        });
//
//});

$(document).ready(function() {

    var $submit = $("#check_rec_ids_btn").hide(), $update_check = $("#update_check").hide(), $update_label = $("#update_label").hide(),
        $cbs = $('input[name="check-box"]').click(function() {
            $submit.toggle( $cbs.is(":checked") ) && $update_check.toggle( $cbs.is(":checked") ) && $update_label.toggle( $cbs.is(":checked") );
        });

});




function del_rec(id) {
    $('#bd-example-modal-sm' + id).modal('show');
    $('#modal_del' + id).attr('href', '')
    $('#modal_del' + id).attr('href', '/delete_record/' + id)
}


function check_box() {
    if ($('.form-check-input').is(":checked"))
        $("#add").hide();

    else
        $("#add").show();


}

function del_fun(){
        $('#stu_ids_submit').click()
    }
function update_fun(){
        $('#class_ids_submit').click()
    }



$(document).ready(function() {

    var $submit = $("#action_dropdown").hide(),
        $cbs = $('input[name="check-box"]').click(function() {
            $submit.toggle( $cbs.is(":checked") );
        });

});




  $("#checkAll").change(function() {
    var checkboxes = document.querySelectorAll('input[type="checkbox"]');
//    var selectAll = document.getElementById("select_all");
    for (var i = 0; i < checkboxes.length; i++) {
        checkboxes[i].checked = !checkboxes[i].checked;
        if(checkboxes[i].checked){
            values.push(checkboxes[i].getAttribute("value"));
            $("#add").hide();
             $("#check_rec_ids_btn").show();
             $update_check = $("#update_check").show();
             $update_label = $("#update_label").show();
             $("#action_dropdown").show()
             document.getElementById("rec_ids").value = values
             document.getElementById("send_rec_ids").value = values
             document.getElementById("check_rec_ids").value = values

        }else{

            var index = values.indexOf(checkboxes[i].getAttribute("value"));
            if (index > -1) {
                values.splice(index, 1);
                $("#add").show();
                $("#check_rec_ids_btn").hide();
                $update_check = $("#update_check").hide();
                $update_label = $("#update_label").hide();
                $("#action_dropdown").hide()
            }
        }
    }
    console.log(values);

});


$(document).ready(function() {
  // Get all rows in the table
  var rows = $("#table-count tr");

  // Iterate through each row
  rows.each(function(index) {
    // Get the specified column
    var column = $(this).find("td:nth-child(2)"); // assumes the 2nd column is the one to be numbered
    // Check if the column exists
    if (column.length) {
      // Add the current index as the column number
      column.text(index);
    }
  });
});

