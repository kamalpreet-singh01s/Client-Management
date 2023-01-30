
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





//
//$(document).ready(function() {
//
//    var $submit = $("#check_rec_ids_btn").hide(), $update_check = $("#update_check").hide(), $update_label = $("#update_label").hide(),
//        $cbs = $('input[name="check-box"]').click(function() {
//            $submit.toggle( $cbs.is(":checked") ) && $update_check.toggle( $cbs.is(":checked") ) && $update_label.toggle( $cbs.is(":checked") );
//        });
//
//});

function toggleDelbox() {
  var elems = document.querySelectorAll('.hidden');
  var shouldShowList = false;
  elems.forEach(function(elem) {
    if (elem.checked) {
      shouldShowList = true;
    }
  });
  document.querySelector('#action_dropdown').style.display = shouldShowList ? '' : 'none';
  document.querySelector('#generate_custom_report').style.display = shouldShowList ? '' : 'none';
  document.querySelector('#add').style.display = shouldShowList ? 'none' : '';
}





//function check_box() {
//    if ($('.form-check-input').is(":checked"))
//        $("#add").hide()
//    else
//        $("#add").show()
//}


function del_fun(){
        $('#stu_ids_submit').click()
    }

//$(document).ready(function() {
//
//    var $submit = $("#action_dropdown").hide(),
//        $cbs = $('input[name="check-box"]').click(function() {
//            $submit.toggle( $cbs.is(":checked") );
//        });
//
//});




  $("#check-All").change(function() {
    var checkboxes = document.querySelectorAll('input[type="checkbox"]');
//    var selectAll = document.getElementById("select_all");
    for (var i = 0; i < checkboxes.length; i++) {
        checkboxes[i].checked = !checkboxes[i].checked;
        if(checkboxes[i].checked){
            cli_values.push(checkboxes[i].getAttribute("value"));
//            $("#add").hide();
//             $("#check_rec_ids_btn").show();
//             $update_check = $("#update_check").show();
//             $update_label = $("#update_label").show();
//             $("#action_dropdown").show()
                var elems = document.querySelectorAll('.hidden');
              var shouldShowList = false;
              elems.forEach(function(elem) {
                if (elem.checked) {
                  shouldShowList = true;
                }
              });
              document.querySelector('#action_dropdown').style.display = shouldShowList ? '' : 'none';
              document.querySelector('#generate_custom_report').style.display = shouldShowList ? '' : 'none';
              document.querySelector('#add').style.display = shouldShowList ? 'none' : '';


            document.getElementById("rec_ids").value = cli_values
            document.getElementById("check_rec_ids").value = cli_values
            var element = document.getElementById("check-All");
             element.checked = true;
        }else{

            var index = cli_values.indexOf(checkboxes[i].getAttribute("value"));
            if (index > -1) {
                cli_values.splice(index, 1);
//                $("#add").show();
//                $("#check_rec_ids_btn").hide();
//                $update_check = $("#update_check").hide();
//                $update_label = $("#update_label").hide();
//                $("#action_dropdown").hide()
                var elems = document.querySelectorAll('.hidden');
              var shouldShowList = false;
              elems.forEach(function(elem) {
                if (elem.checked) {
                  shouldShowList = true;
                }
              });
              document.querySelector('#action_dropdown').style.display = shouldShowList ? '' : 'none';
              document.querySelector('#generate_custom_report').style.display = shouldShowList ? '' : 'none';
              document.querySelector('#add').style.display = shouldShowList ? 'none' : '';

                var element = document.getElementById("check-All");
             element.checked = false;
            }
        }
    }
    console.log(cli_values);
    console.log(document.getElementById("check-All").checked)
});


$(document).ready(function() {
  var rows = $("#table-count tr");
  rows.each(function(index) {
    var column = $(this).find("td:nth-child(2)");
    if (column.length) {
      column.text(index);
    }
  });
});