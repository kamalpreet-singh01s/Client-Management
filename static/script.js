
var status = document.querySelectorAll("status").innerText;


$(document).ready(function(){
    $( ".status:contains('Pending')" ).css( "color", "white" );
    $( ".status:contains('Pending')" ).css( "background-color", "red" );
    $( ".status:contains('Pending')" ).css( "font-weight" , "bold" );
})

$(document).ready(function(){
    $( ".status:contains('Cancel')" ).css( "color", "black" );
    $( ".status:contains('Cancel')" ).css( "background-color", "#8e8df4" );
    $( ".status:contains('Cancel')" ).css( "font-weight" , "bold" );
})

$(document).ready(function(){
    $( ".status:contains('Received')" ).css( "color", "white" );
    $( ".status:contains('Received')" ).css( "background-color", "green" );
    $( ".status:contains('Received')" ).css( "font-weight" , "bold" );
})