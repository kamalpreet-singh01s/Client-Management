//function check_box() {
//    if ($('.form-check-input').is(":checked"))
//        $("#add").hide()
//    else
//        $("#add").show()
//}

function toggleDelbox() {
  var elems = document.querySelectorAll('.hidden');
  var shouldShowList = false;
  elems.forEach(function(elem) {
    if (elem.checked) {
      shouldShowList = true;
    }
  });
  document.querySelector('#action_dropdown').style.display = shouldShowList ? '' : 'none';
//  document.querySelector('#generate_custom_report').style.display = shouldShowList ? '' : 'none';
  document.querySelector('#add').style.display = shouldShowList ? 'none' : '';
}

//$(document).ready(function() {
//
//    var $submit = $("#action_dropdown").hide(),
//        $cbs = $('input[name="check-box"]').click(function() {
//            $submit.toggle( $cbs.is(":checked") );
//        });
//
//});

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


