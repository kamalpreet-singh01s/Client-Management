
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
  document.querySelector('#filter').style.display = shouldShowList ? 'none' : '';
}



function del_rec(id) {
    $('#bd-example-modal-sm' + id).modal('show');
    $('#modal_del' + id).attr('href', '')
    $('#modal_del' + id).attr('href', '/delete_record/' + id)
}



function del_fun(){
        $('#stu_ids_submit').click()
    }
function update_fun(){
        $('#class_ids_submit').click()
    }




var status = document.querySelectorAll("status").innerText;


$(document).ready(function(){
    $( ".status:contains('Pending')" ).css( "color", "white" );
    $( ".status:contains('Pending')" ).css( "background-color", "#ffc107" );
    $( ".status:contains('Pending')" ).css( "font-weight" , "bold" );
    $( ".status:contains('Pending')" ).css( "border-radius" , "20px" );
    $( ".status:contains('Pending')" ).css( "padding" , "4px 11px" );
})

$(document).ready(function(){
    $( ".status:contains('Cancel')" ).css( "color", "white" );
    $( ".status:contains('Cancel')" ).css( "background-color", "red" );
    $( ".status:contains('Cancel')" ).css( "font-weight" , "bold" );
    $( ".status:contains('Cancel')" ).css( "border-radius" , "20px" );
    $( ".status:contains('Cancel')" ).css( "padding" , "4px 11px" );

})

$(document).ready(function(){
    $( ".status:contains('Received')" ).css( "color", "white" );
    $( ".status:contains('Received')" ).css( "background-color", "green" );
    $( ".status:contains('Received')" ).css( "font-weight" , "bold" );
    $( ".status:contains('Received')" ).css( "border-radius" , "20px" );
    $( ".status:contains('Received')" ).css( "padding" , "4px 11px" );

})




$(document).ready(function () {
    $('#check-All').click(function (event) {
        if (this.checked) {
            $('.form-check-input').each(function () { //loop through each checkbox
                $(this).prop('checked', true); //check
                values.push($(this).val());
                textbox.value = values
                textbox2.value = values
                textbox3.value = values


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
              document.querySelector('#filter').style.display = shouldShowList ? 'none' : '';

            });
        } else {
            $('.form-check-input').each(function () { //loop through each checkbox
                $(this).prop('checked', false); //uncheck
                values = []
                textbox.value = values
                textbox2.value = values
                textbox3.value = values

                var elems = document.querySelectorAll('.hidden');
              var shouldShowList = false;
              elems.forEach(function(elem) {
                if (elem.checked) {
                  shouldShowList = true;
                }
              });
              document.querySelector('#action_dropdown').style.display = shouldShowList ? '' : 'none';
              document.querySelector('#generate_custom_report').style.display = shouldShowList ? '' : 'none';
              document.querySelector('#add').style.display = shouldShowList ? '' : 'block';
              document.querySelector('#filter').style.display = shouldShowList ? 'none' : '';

            });
        }
        console.log(values)
    });
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



