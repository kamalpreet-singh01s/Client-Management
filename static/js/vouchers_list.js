
$(document).ready(function(){
    $( ".status:contains('Draft')" ).css( "color", "white" );
    $( ".status:contains('Draft')" ).css( "background-color", "#ffc107" );
    $( ".status:contains('Draft')" ).css( "font-weight" , "bold" );
       $( ".status:contains('Draft')" ).css( "border-radius" , "20px" );
    $( ".status:contains('Draft')" ).css( "padding" , "4px 5px" );
})

$(document).ready(function(){
    $( ".status:contains('Cancelled')" ).css( "color", "white" );
    $( ".status:contains('Cancelled')" ).css( "background-color", "red" );
    $( ".status:contains('Cancelled')" ).css( "font-weight" , "bold" );
       $( ".status:contains('Cancelled')" ).css( "border-radius" , "20px" );
    $( ".status:contains('Cancelled')" ).css( "padding" , "4px 5px" );
})

$(document).ready(function(){
    $( ".status:contains('Approved')" ).css( "color", "white" );
    $( ".status:contains('Approved')" ).css( "background-color", "green" );
    $( ".status:contains('Approved')" ).css( "font-weight" , "bold" );
       $( ".status:contains('Approved')" ).css( "border-radius" , "20px" );
    $( ".status:contains('Approved')" ).css( "padding" , "4px 5px" );
})

//
//function check_box() {
//    if ($('.form-check-input').is(":checked"))
//        $("#add").hide()
//    else
//        $("#add").show()
//}

//$(document).ready(function() {
//
//    var $submit = $("#action_dropdown").hide(),
//        $cbs = $('input[name="check-box"]').click(function() {
//            $submit.toggle( $cbs.is(":checked") );
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

}




var voucher_ids = [];
textbox2 = document.getElementById("rec_ids")

$(".form-check-input").click(function(){
    voucher_ids=[];
    $(".form-check-input").each(function(){
        if($(this).is(":checked")){
        voucher_ids.push($(this).val());
        }
        });
        console.log(voucher_ids);
        textbox2.value = voucher_ids

    });


function del_fun(){
    $('#stu_ids_submit').click()
}


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