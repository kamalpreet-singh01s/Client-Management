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
